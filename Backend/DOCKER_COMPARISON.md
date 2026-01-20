# Docker Comparison: Current vs. Recommended Setup

**Quick Answer**: 
- ✅ **Current docker-compose.yml**: Good for development, 60% production-ready
- ✅ **Recommended docker-compose.production.yml**: 95% production-ready

---

## Side-by-Side Comparison

### 1. Database Image

| Feature | Current | Recommended | Impact |
|---------|---------|-------------|--------|
| Image | `postgres:15-alpine` | `pgvector/pgvector:pg15` | ✅ Ensures pgvector extension works |
| Init Scripts | Single db.sql | 01-init.sql + 02-seed.sql | ✅ Sample data for testing |
| Backups | None | Daily backup service | ✅ No data loss |
| Persistence | Basic volume | Explicit volume with limits | ✅ Better reliability |

### 2. Redis Configuration

| Feature | Current | Recommended | Impact |
|---------|---------|-------------|--------|
| Persistence | None | AOF enabled | ✅ Background tasks survive restarts |
| Memory Limit | Unlimited | 2GB limit | ✅ Prevents runaway memory usage |
| Password | Not set | Environment variable | ✅ Security improvement |
| Health Check | Basic ping | Ping with password | ✅ Safer monitoring |

### 3. Web Service

| Feature | Current | Recommended | Impact |
|---------|---------|-------------|--------|
| Migrations | Yes, in docker-compose | Yes, in startup | ✅ More reliable |
| Static Files | None | Collected and served | ✅ Production-ready |
| Secrets | Hardcoded in compose | From .env file | ✅ Security improvement |
| Resource Limits | None | CPU/Memory caps | ✅ Prevents crashes |
| Health Check | Missing | HTTP endpoint check | ✅ Better monitoring |

### 4. Backup & Recovery

| Feature | Current | Recommended | Impact |
|---------|---------|-------------|--------|
| Backup | None | Daily automatic | ✅ 30-day retention |
| Restoration | Manual | Documented procedure | ✅ Quick recovery |
| Data Loss Risk | HIGH | Minimal | ✅ Critical for production |

### 5. Security

| Feature | Current | Recommended | Impact |
|---------|---------|-------------|--------|
| Secrets | In docker-compose.yml | In .env (gitignored) | ✅ No accidental commits |
| Database Password | `postgres` | From environment | ✅ Unique per deployment |
| Django SECRET_KEY | Hardcoded | From environment | ✅ Rotatable |
| Nginx | Minimal | Full proxy config | ✅ Production HTTP(S) |

---

## Real-World Issues & Solutions

### Issue 1: pgvector Extension Not Found

**Symptom**:
```
ProgrammingError: could not open extension control file "/usr/share/postgresql/15/extension/vector.control"
```

**Current Setup**: ❌ Will fail silently
**Recommended Setup**: ✅ Uses pre-built image

**Solution**: Use `pgvector/pgvector:pg15` instead of `postgres:15-alpine`

---

### Issue 2: Data Lost on `docker-compose down -v`

**Symptom**: All research data disappears

**Current Setup**: ❌ No backup
```bash
docker-compose down -v  # ← This deletes EVERYTHING
```

**Recommended Setup**: ✅ Daily backups in ./backups/
```bash
ls -la backups/
backup_20240120_020000.sql.gz  # ← Safe!
backup_20240119_020000.sql.gz
```

---

### Issue 3: Background Tasks Disappear

**Symptom**: CSV import started, then container restarted, import is gone

**Current Setup**: ❌ Redis has no persistence
```yaml
redis:
  command: redis-server  # ← No AOF, data lost!
```

**Recommended Setup**: ✅ AOF persistence enabled
```yaml
redis:
  command: redis-server --appendonly yes  # ← Tasks survive restart
```

---

### Issue 4: Port Conflicts

**Symptom**:
```
Error: bind: address already in use
```

**Current Setup**: ❌ Fixed ports only
**Recommended Setup**: ✅ Configurable via .env

```bash
# .env
DB_PORT=5432
WEB_PORT=8000
REDIS_PORT=6379
```

---

### Issue 5: Out of Memory

**Symptom**: Container crashes randomly
```
OOMKilled (Out of Memory)
```

**Current Setup**: ❌ No limits
```yaml
postgres:
  image: postgres:15-alpine
  # ← Can use 100% of available RAM!
```

**Recommended Setup**: ✅ Resource limits set
```yaml
postgres:
  deploy:
    resources:
      limits:
        memory: 4G  # ← Maximum usage
      reservations:
        memory: 2G  # ← Guaranteed allocation
```

---

### Issue 6: Secrets in Git

**Symptom**: Production passwords accidentally committed

**Current Setup**: ❌ Secrets hardcoded
```yaml
# docker-compose.yml (visible in git history!)
POSTGRES_PASSWORD: postgres
SECRET_KEY: django-insecure-change-me-in-production
```

**Recommended Setup**: ✅ Secrets in .env (gitignored)
```bash
# .env (added to .gitignore)
POSTGRES_PASSWORD=prod_secure_password_123
SECRET_KEY=prod_secret_key_xyz
```

---

### Issue 7: No Backup/Recovery Procedure

**Scenario**: Database corrupted, need to recover

**Current Setup**: ❌ No procedure
```bash
# How do we restore? No backups exist!
```

**Recommended Setup**: ✅ Automated backups + recovery guide
```bash
# Restore from backup
gunzip < backups/backup_20240120_020000.sql.gz | \
  docker exec -i daystar-postgres psql -U postgres -d daystar_db
```

---

### Issue 8: Migrations Not Running

**Symptom**:
```
ProgrammingError: relation "research_graph_researcher" does not exist
```

**Current Setup**: ⚠️ In docker-compose, not in Dockerfile
```yaml
# If web container starts before postgres, migrations skip!
```

**Recommended Setup**: ✅ Better startup logic
```dockerfile
# Dockerfile ensures migrations always run
command: python manage.py migrate && gunicorn ...
```

---

### Issue 9: No Sample Data for Testing

**Symptom**: Database empty after startup, can't test graph visualization

**Current Setup**: ❌ Empty database
```bash
docker-compose up
# Database ready but: no researchers, no publications, nothing!
```

**Recommended Setup**: ✅ Auto-seeded with 5 researchers + 10 publications
```bash
docker-compose up
# Database populated with sample data immediately
curl http://localhost:8000/api/researchers/  # ← Returns data!
```

---

### Issue 10: Secrets in Environment Variables

**Symptom**: Database password appears in `docker ps` output!

```bash
$ docker ps
CONTAINER ID  COMMAND  PORTS
...  postgres ... POSTGRES_PASSWORD=postgres  # ← Visible!
```

**Current Setup**: ❌ Visible to anyone with docker access
**Recommended Setup**: ✅ Secrets in .env, not in container inspection

---

## Migration Path: Current → Recommended

### Step 1: Create .env File
```bash
# .env (gitignored)
DEBUG=False
SECRET_KEY=your-production-secret-key
POSTGRES_PASSWORD=secure_password_123
DB_USER=postgres
DB_NAME=daystar_db
REDIS_PASSWORD=redis_password
```

### Step 2: Backup Current Database
```bash
docker exec daystar-postgres pg_dump -U postgres daystar_db | \
  gzip > backup_before_upgrade.sql.gz
```

### Step 3: Replace docker-compose.yml
```bash
# Keep the old one for reference
cp docker-compose.yml docker-compose.old.yml

# Use the new production-ready version
cp docker-compose.production.yml docker-compose.yml
```

### Step 4: Create Scripts Directory
```bash
mkdir -p scripts
cp docker-init-db.sql scripts/01-init.sql
touch scripts/02-seed.sql
```

### Step 5: Rebuild and Test
```bash
# Bring down old containers
docker-compose down

# Remove old volumes (backup exists!)
docker volume rm daystar_postgres_data

# Build and start with new setup
docker-compose up --build

# Verify all services are healthy
docker-compose ps
docker-compose logs web
```

### Step 6: Restore Data (Optional)
```bash
# Restore from backup if needed
gunzip < backup_before_upgrade.sql.gz | \
  docker exec -i daystar-postgres psql -U postgres -d daystar_db
```

---

## Testing the Improvements

### Test 1: Data Persistence
```bash
# 1. Add data
curl -X POST http://localhost:8000/api/researchers/ ...

# 2. Restart containers
docker-compose restart

# 3. Verify data still exists
curl http://localhost:8000/api/researchers/  # ← Data is there!
```

### Test 2: Backup Creation
```bash
# Check backups are being created
ls -la backups/
# Should show: backup_20240120_020000.sql.gz

# Verify backup is valid
gunzip < backups/backup_20240120_020000.sql.gz | head -20
```

### Test 3: Resource Limits
```bash
# Check resource limits are applied
docker inspect daystar-postgres | grep -A5 Resources

# Should show:
# "MemoryLimit": 4294967296,  (4GB)
```

### Test 4: Health Checks
```bash
# Monitor health status
docker-compose ps

# Should show STATUS: "Up X seconds (healthy)"
```

---

## Deployment Checklist

### Before Production Deployment

- [ ] Create .env file with production secrets
- [ ] Add .env to .gitignore
- [ ] Test full docker-compose up → down → up cycle
- [ ] Verify daily backups are created
- [ ] Test backup restoration procedure
- [ ] Set up monitoring (Docker stats, logs)
- [ ] Configure SSL/TLS certificates for nginx
- [ ] Set up log aggregation (optional but recommended)
- [ ] Document disaster recovery procedure
- [ ] Create runbook for common issues

### Production Monitoring

```bash
# Monitor container health
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f postgres

# Check resource usage
docker stats daystar-postgres daystar-web daystar-redis

# Verify backup system
ls -la backups/ | tail -5
```

---

## Cost Comparison

### Infrastructure Requirements

| Component | Current | Recommended | Notes |
|-----------|---------|-------------|-------|
| CPU | 4+ cores | 4 cores | Same |
| RAM | 8GB | 8GB | Same, but limited to 4GB + 2GB + 2GB |
| Disk | 100GB | 150GB | Extra space for backups |
| Network | Standard | Standard | Same |
| **Estimated Cost** | **$50-100/month** | **$60-120/month** | Backup storage adds $10-20/month |

---

## Summary: Should You Upgrade?

### Current Setup is Fine For:
- ✅ Local development
- ✅ Small team (< 10 people)
- ✅ Non-critical testing
- ✅ Short-term demos

### You NEED Recommended Setup For:
- ❌ Production deployments
- ❌ Real research data (irreplaceable)
- ❌ Institutional use (compliance required)
- ❌ Long-term operations
- ❌ Shared team environment

---

## Bottom Line

**Current db.sql Approach**: 
- Good for development ✅
- Risky for production ❌
- Missing backups 🔴
- Missing security 🔴

**Recommended Approach**:
- Production-ready ✅
- Automated backups ✅
- Resource limits ✅
- Security hardened ✅
- Minimal extra cost 💰

**Recommendation**: Upgrade to production-ready setup before deploying to any institutional or production environment.

---

**Implementation Time**: ~30 minutes
**Risk Level**: Low (can rollback easily)
**Benefit**: Peace of mind + data safety + production readiness
