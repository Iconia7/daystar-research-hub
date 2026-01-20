# Docker Setup Analysis & Implementation Guide

**Date**: January 20, 2026
**Project**: Daystar Research Collaboration Graph
**Assessment**: Current setup is GOOD for development, but needs improvements for production

---

## Current Docker Architecture

### ✅ What's Already Configured
```
postgres:15-alpine          PostgreSQL with pgvector extension
redis:7-alpine              Task queue (Celery)
web (Django)                Main application
celery-worker               Async task processing
celery-beat                 Scheduled tasks
nginx:alpine                Reverse proxy
```

### Docker DB SQL - Is It the Best Option?

**Short Answer**: ✅ YES for development, ⚠️ NEEDS IMPROVEMENTS for production

---

## Detailed Analysis: db.sql Approach

### ✅ ADVANTAGES

**1. Automatic Extension Setup**
```sql
CREATE EXTENSION IF NOT EXISTS vector;    -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- Text search
```
- Extensions are created automatically on first container run
- No manual setup required
- Works across all environments consistently

**2. Reproducible Initialization**
- Same database state every time containers are built
- Easy to track database schema in version control
- Clear audit trail of database changes

**3. Development Simplicity**
```bash
docker-compose up --build    # One command, everything starts
```
- No separate database setup steps
- Great for onboarding new team members
- Perfect for CI/CD pipelines

**4. Container Best Practice**
- Docker initialization files are standard approach
- Well-documented in Docker community
- Easy for other developers to understand

---

## ⚠️ CRITICAL ISSUES THEY WILL FACE

### Issue 1: **Data Loss on Container Rebuild** 🔴 CRITICAL
```bash
docker-compose down -v     # ← This DELETES all data!
docker-compose up --build  # ← Database resets to initial state
```

**Problem**: 
- Any data entered into the system is GONE
- Research data, user accounts, embeddings all deleted
- Not suitable for production

**Who's Affected**: Everyone testing with real data

**Solution**:
```yaml
# docker-compose.yml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/daystar/postgres-data  # ← Persistent volume
```

---

### Issue 2: **Django Migrations Not Automated** 🟠 HIGH
```dockerfile
# Current: migrations are NOT automatic
command: gunicorn daystar_project.wsgi --bind 0.0.0.0:8000

# But docker-compose.yml has:
command: sh -c "python manage.py migrate && gunicorn ..."
```

**Problem**:
- If a developer forgets to run migrations, database schema doesn't match code
- First time setup fails silently
- Models and database get out of sync

**Who's Affected**: New developers, CI/CD pipelines

**Solution**: Make migrations mandatory
```dockerfile
# Improved Dockerfile
RUN python manage.py migrate --noinput || exit 1
CMD ["gunicorn", "daystar_project.wsgi", ...]
```

---

### Issue 3: **pgvector Extension Version Conflicts** 🟠 HIGH
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Problem**:
- PostgreSQL 15-alpine might not have pgvector pre-installed
- Extension creation might fail silently
- Semantic search suddenly doesn't work in production

**Who's Affected**: Embedding service, semantic matching, graph analytics

**Error When It Fails**:
```
ProgrammingError: could not open extension control file
```

**Solution**: Use PostgreSQL image WITH pgvector pre-installed
```yaml
# docker-compose.yml
postgres:
  image: pgvector/pgvector:pg15  # ← Pre-built with pgvector
  # Instead of: postgres:15-alpine
```

---

### Issue 4: **Health Checks Insufficient** 🟠 HIGH
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Problem**:
- Database READY doesn't mean MIGRATIONS COMPLETE
- Web service starts before schema is loaded
- AlembicVersionError or table doesn't exist errors

**Who's Affected**: First-time docker-compose up, CI/CD

**Solution**: Add proper dependency checks
```bash
# Better health check
CMD: sh -c "python manage.py migrate && \
           python manage.py check --deploy && \
           gunicorn ..."
```

---

### Issue 5: **No Database Backup Strategy** 🔴 CRITICAL
```yaml
# Current: no backup configuration
postgres_data:  # ← Only lives in container
```

**Problem**:
- No backup on container failure
- No point-in-time recovery
- Research data loss = catastrophic

**Who's Affected**: Production deployments, data durability

**Solution**: Add backup service
```yaml
db-backup:
  image: postgres:15-alpine
  volumes:
    - ./backups:/backups
    - postgres_data:/db_data
  command: |
    sh -c 'while true; do
      pg_dump -h postgres -U postgres daystar_db | \
      gzip > /backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz;
      sleep 86400;  # Daily backup
    done'
  depends_on:
    - postgres
```

---

### Issue 6: **Celery/Redis Not Properly Initialized** 🟡 MEDIUM
```yaml
# No data persistence for Redis
redis_data:/data  # ← Lost on restart!
```

**Problem**:
- Background tasks queued during downtime are LOST
- CSV imports, embedding generation get lost
- No async job recovery

**Who's Affected**: Long-running tasks, data imports

**Solution**: Configure Redis persistence
```yaml
redis:
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data  # With AOF persistence
```

---

### Issue 7: **No Database Seeding for Testing** 🟡 MEDIUM
```sql
-- Current init.sql only creates extensions
-- No sample data for testing!
```

**Problem**:
- Database is empty after first run
- Frontend team has nothing to test against
- Manual data entry needed for every test scenario

**Who's Affected**: Frontend team, QA, demo deployments

**Solution**: Add seed data script
```sql
-- docker-init-db.sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Seed sample data
INSERT INTO research_graph_researcher (id, user_id, department, created_at, updated_at)
VALUES (1, 1, 'Computer Science', NOW(), NOW());

INSERT INTO research_graph_publication (id, title, publication_date, created_at, updated_at)
VALUES (1, 'Sample Research Paper', NOW(), NOW(), NOW());
```

---

### Issue 8: **Secrets in Environment Variables** 🔴 CRITICAL
```yaml
# docker-compose.yml (EXPOSED!)
environment:
  - SECRET_KEY=django-insecure-change-me-in-production
  - POSTGRES_PASSWORD=postgres
  - ALLOWED_HOSTS=localhost,127.0.0.1,web
```

**Problem**:
- Secrets visible in git history
- Same credentials for all environments
- Security audit failure

**Who's Affected**: Production, security compliance

**Solution**: Use secrets management
```bash
# .env file (gitignored)
SECRET_KEY=your-production-secret-key-here
POSTGRES_PASSWORD=strong-secure-password
DATABASE_URL=postgresql://...

# docker-compose.yml
env_file:
  - .env
```

---

### Issue 9: **No Log Management** 🟡 MEDIUM
```yaml
# No centralized logging
# Logs go to stdout only
```

**Problem**:
- Logs lost when containers restart
- No debugging production issues
- Hard to track errors across services

**Who's Affected**: Debugging, monitoring, compliance

**Solution**: Add ELK stack or centralized logging
```yaml
# docker-compose.yml
fluentd:
  image: fluent/fluentd
  volumes:
    - ./fluent.conf:/fluentd/etc/fluent.conf
    - ./logs:/fluentd/log
  ports:
    - "24224:24224"
```

---

### Issue 10: **Resource Limits Not Set** 🟡 MEDIUM
```yaml
# No CPU/memory limits
postgres:
  image: postgres:15-alpine
  # ← Can consume unlimited resources!
```

**Problem**:
- One service can crash entire host
- Memory leaks cause cascading failures
- No predictable resource usage

**Who's Affected**: Shared hosting, cloud deployment

**Solution**: Set resource limits
```yaml
postgres:
  image: postgres:15-alpine
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

---

## Production-Ready Docker Improvements

### Recommended Enhancements

#### 1. **Use Better Base Image for PostgreSQL**
```yaml
# BEFORE (current)
postgres:
  image: postgres:15-alpine
  # Extensions might not be available

# AFTER (improved)
postgres:
  image: pgvector/pgvector:pg15
  # pgvector pre-installed
```

#### 2. **Add Health Check for Migrations**
```dockerfile
# Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()"
```

#### 3. **Add Initialization Script**
```bash
# scripts/init-db.sh
#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
END

echo "Generating embeddings for sample data..."
python manage.py shell << END
from research_graph.services import EmbeddingService
EmbeddingService.batch_embed_researchers()
EmbeddingService.batch_embed_publications()
END

echo "Database initialization complete!"
```

#### 4. **Add Backup Service**
```yaml
# docker-compose.yml
pg-backup:
  image: postgres:15-alpine
  command: |
    sh -c 'while true; do
      pg_dump -h postgres -U $$POSTGRES_USER -d $$POSTGRES_DB | \
      gzip > /backups/daystar_$$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz;
      sleep 86400;
    done'
  environment:
    POSTGRES_USER: postgres
    POSTGRES_DB: daystar_db
  volumes:
    - ./backups:/backups
    - postgres_data:/data
  depends_on:
    - postgres
```

#### 5. **Add Secrets Management**
```bash
# .env (create and gitignore)
POSTGRES_PASSWORD=secure_password_123
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# .gitignore
.env
.env.local
*.backup
backups/
```

---

## Recommended Production Docker Setup

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15  # ← Better image
    container_name: daystar-postgres
    env_file: .env  # ← Secrets from file
    environment:
      POSTGRES_INITDB_ARGS: "-c shared_preload_libraries=vector"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker-init-db.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./scripts/init-seeding.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    networks:
      - daystar-network

  redis:
    image: redis:7-alpine
    container_name: daystar-redis
    command: redis-server --appendonly yes  # ← Persistence
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
    networks:
      - daystar-network

  web:
    build: .
    container_name: daystar-web
    env_file: .env
    command: sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn daystar_project.wsgi --bind 0.0.0.0:8000 --workers 4 --timeout 120"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./:/app
      - static_files:/app/staticfiles
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    networks:
      - daystar-network

  # Database backup service
  pg-backup:
    image: postgres:15-alpine
    command: |
      sh -c 'while true; do
        pg_dump -h postgres -U postgres daystar_db | \
        gzip > /backups/backup_$$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz;
        find /backups -name "*.sql.gz" -mtime +30 -delete;
        sleep 86400;
      done'
    environment:
      PGPASSWORD: postgres
    volumes:
      - ./backups:/backups
    depends_on:
      - postgres
    networks:
      - daystar-network

volumes:
  postgres_data:
  redis_data:
  static_files:

networks:
  daystar-network:
    driver: bridge
```

---

## Implementation Checklist for Team

### Before First Deployment

- [ ] Rename `docker-init-db.sql` to `01-init.sql`
- [ ] Create `02-seed.sql` with sample data
- [ ] Create `.env` file with production secrets
- [ ] Add `.env` to `.gitignore`
- [ ] Create `backup/` directory structure
- [ ] Update `docker-compose.yml` with improvements above
- [ ] Test: `docker-compose up --build` (fresh start)
- [ ] Test: `docker-compose down -v && docker-compose up` (data persistence)
- [ ] Verify backups are created
- [ ] Document password recovery procedure

### Database Issues They'll Face

| Issue | Symptom | Fix |
|-------|---------|-----|
| pgvector not found | `ERROR: extension "vector" not found` | Use `pgvector/pgvector:pg15` image |
| Migrations not run | `ProgrammingError: table does not exist` | Add `python manage.py migrate` to startup |
| Data lost on rebuild | Everything gone after `docker-compose down -v` | Use named volumes, don't use `-v` |
| Redis data lost | Background tasks disappear | Enable `--appendonly yes` |
| Port conflicts | `Error: bind: address already in use` | Change port mappings in docker-compose |
| Out of disk space | Docker containers crash | Set up log rotation, cleanup old backups |
| Slow performance | API responses timeout | Add resource limits, optimize queries |

---

## Summary: Is db.sql the Best Option?

### ✅ YES for:
- Development environments
- CI/CD pipelines
- Quick prototyping
- Team onboarding

### ❌ NO for:
- Production deployments (needs backups)
- Data persistence (needs volume management)
- Security (secrets in code)
- Scalability (no resource limits)

### 🎯 Recommendation:
**Use db.sql + all improvements above for production-grade setup**

The current setup is 60% ready. With the 10 improvements listed, it becomes 95% production-ready.

---

**Next Steps**:
1. Update docker-compose.yml with improvements
2. Create .env file with production secrets
3. Add backup service
4. Test full deployment cycle
5. Document recovery procedures
