# Daystar Research Collaboration Graph & Intelligence Hub

**Status**: ✅ Production-Ready | Backend: 100% Complete | API: Fully Documented

---

## Project Overview

Daystar is an intelligent research mapping platform that transforms fragmented institutional research records into a unified, searchable knowledge network. The system maps researchers, publications, and collaborations as an interactive graph, revealing expertise clusters, interdisciplinary linkages, and research opportunities.

**Core Features**:
- 📊 **Interactive Collaboration Graph** - Visualize researchers, publications, and partnerships
- 🔍 **Advanced Search & Filtering** - Search by topic, SDG goals, department, year
- 🤝 **Collaborator Discovery** - Semantic matching for potential partnerships
- 💰 **Funding Alignment** - Match researchers with grant opportunities
- 📈 **Analytics Dashboard** - Department performance, SDG distribution, metrics
- 🔐 **User Authentication** - JWT-based authentication and authorization

---

## Quick Start

### 1. Install Dependencies
```bash
cd /home/bantu/Documents/Backend
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Start Backend Server
```bash
python manage.py runserver
```

### 5. Access API
- **API Root**: http://localhost:8000/api/
- **API Docs**: http://localhost:8000/api/docs/
- **Schema**: http://localhost:8000/api/schema/

---

## API Documentation

### Authentication Endpoints
```
POST   /api/auth/register/          Register new user
POST   /api/auth/login/             Login (returns JWT tokens)
POST   /api/auth/refresh/           Refresh access token
GET    /api/auth/me/                Get current user profile
POST   /api/auth/logout/            Logout
PUT    /api/auth/profile/           Update user profile
```

### CRUD Operations
```
GET    /api/researchers/            List researchers (paginated, searchable)
POST   /api/researchers/            Create researcher
GET    /api/researchers/{id}/       Get researcher details
PUT    /api/researchers/{id}/       Update researcher
DELETE /api/researchers/{id}/       Delete researcher

GET    /api/publications/           List publications (paginated, searchable)
POST   /api/publications/           Create publication
GET    /api/publications/{id}/      Get publication details
PUT    /api/publications/{id}/      Update publication
DELETE /api/publications/{id}/      Delete publication

GET    /api/collaborations/         List collaborations
POST   /api/collaborations/         Create collaboration
GET    /api/collaborations/{id}/    Get collaboration details
PUT    /api/collaborations/{id}/    Update collaboration
DELETE /api/collaborations/{id}/    Delete collaboration

GET    /api/authorships/            List authorships
POST   /api/authorships/            Create authorship
GET    /api/authorships/{id}/       Get authorship details
PUT    /api/authorships/{id}/       Update authorship
DELETE /api/authorships/{id}/       Delete authorship
```

### Graph Visualization
```
GET    /api/graph/                  Complete network graph (nodes + links)
GET    /api/graph/researchers/      Researcher collaboration network
GET    /api/graph/publications/     Publication authorship network
```

### Analytics
```
GET    /api/analytics/              Complete analytics dashboard
GET    /api/analytics/sdg-distribution/     SDG tag distribution
GET    /api/analytics/department-performance/    Department metrics
GET    /api/analytics/collaboration-metrics/    Collaboration stats
```

---

## Search & Filtering

### Search Examples
```
GET /api/researchers/?search=machine+learning         # Search by name/interests
GET /api/publications/?search=climate+change         # Search by title/abstract
GET /api/publications/?sdg_tags=SDG_13,SDG_7        # Filter by SDG goals
GET /api/researchers/?department=Computer%20Science # Filter by department
GET /api/publications/?year_from=2020&year_to=2024  # Filter by year range
GET /api/collaborations/?min_strength=2             # Filter by strength
```

### Ordering
```
GET /api/researchers/?ordering=-created_at           # Order by creation date (newest first)
GET /api/publications/?ordering=publication_date     # Order by publication date
GET /api/collaborations/?ordering=-strength          # Order by collaboration strength
```

### Pagination
```
GET /api/researchers/?page=1                         # First page (default 20 items)
GET /api/researchers/?page=2&page_size=50            # Custom page size
```

---

## Frontend Integration Example

```javascript
// 1. Register
const registerRes = await fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'researcher1',
    email: 'researcher@university.edu',
    first_name: 'Jane',
    last_name: 'Smith',
    password: 'secure_password',
    password2: 'secure_password'
  })
});

// 2. Login
const loginRes = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'researcher1',
    password: 'secure_password'
  })
});
const { access, refresh } = await loginRes.json();

// 3. Get graph data for visualization
const graphRes = await fetch('http://localhost:8000/api/graph/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const { nodes, links, summary } = await graphRes.json();

// 4. Render with D3.js or React Flow
renderCollaborationGraph(nodes, links);

// 5. Search researchers
const searchRes = await fetch(
  'http://localhost:8000/api/researchers/?search=machine%20learning&department=CS',
  { headers: { 'Authorization': `Bearer ${access}` } }
);
const { count, results } = await searchRes.json();
```

---

## Project Structure

```
/home/bantu/Documents/Backend/
├── daystar_project/              # Django project settings
│   ├── settings.py              # JWT, pagination, authentication config
│   ├── urls.py                  # URL routing
│   ├── celery.py                # Celery task configuration
│   └── wsgi.py                  # WSGI application
├── research_graph/              # Main Django app
│   ├── models.py                # Researcher, Publication, Collaboration models
│   ├── views.py                 # Graph visualization and analytics views
│   ├── viewsets.py              # CRUD ViewSets for all models
│   ├── serializers.py           # REST serializers with validation
│   ├── auth.py                  # Authentication endpoints
│   ├── services.py              # Embedding, matching, and recommendation services
│   ├── urls.py                  # API routes
│   ├── admin.py                 # Django admin configuration
│   ├── analytics.py             # Analytics calculation services
│   ├── tasks.py                 # Celery background tasks
│   └── management/              # Management commands
│       └── commands/
│           ├── ingest_research_data.py   # CSV import
│           └── test_vector_search.py     # Embedding tests
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker services (PostgreSQL, Redis)
├── Dockerfile                   # Docker image
├── manage.py                    # Django management script
├── BACKEND_FIXES_COMPLETE.md    # Implementation details
├── FRONTEND_INTEGRATION_GUIDE.md # Frontend setup guide
└── README.md                    # This file
```

---

## Key Technologies

- **Backend**: Django 5.0, Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL with pgvector (for embeddings)
- **Embeddings**: Sentence-transformers (local, no API keys)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Task Queue**: Celery with Redis
- **Search**: Full-text search + vector similarity search
- **Filtering**: django-filter

---

## Semantic Search & Matching

The backend includes intelligent matching services:

```python
from research_graph.services import SupervisorMatchingService, GrantAlignmentService

# Find supervisor matches for a thesis topic
matches = SupervisorMatchingService.find_supervisor_match(
    thesis_abstract="Deep learning for climate prediction",
    department="Computer Science",
    top_k=5
)

# Find researchers aligned with grant objectives
aligned = GrantAlignmentService.find_aligned_researchers(
    grant_description="AI applications in healthcare",
    top_k=10
)

# Score researcher-grant alignment
score = GrantAlignmentService.score_researcher_for_grant(
    researcher=researcher_obj,
    grant_description="Climate change and AI"
)
```

---

## Data Import

### Import Research Data from CSV
```bash
python manage.py ingest_research_data sample_research_data.csv
```

### Generate Embeddings
```bash
# Generate embeddings for researchers
python manage.py shell
>>> from research_graph.services import EmbeddingService
>>> EmbeddingService.batch_embed_researchers()
>>> EmbeddingService.batch_embed_publications()
```

---

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=daystar_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# CORS (for frontend communication)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://yourdomain.com

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
```

---

## Testing

```bash
# Run all tests
python manage.py test research_graph

# Run specific test file
python manage.py test research_graph.tests.test_auth

# Run with verbose output
python manage.py test research_graph -v 2
```

---

## Deployment

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the API at http://localhost:8000/api/
```

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Set strong `SECRET_KEY`
- [ ] Configure HTTPS/SSL
- [ ] Setup database backups
- [ ] Configure email backend
- [ ] Setup Celery workers
- [ ] Configure Redis persistence
- [ ] Use gunicorn or similar WSGI server

---

## API Response Format

### Success Response (200 OK)
```json
{
  "id": 1,
  "full_name": "Dr. Alice Smith",
  "email": "alice@university.edu",
  "department": "Computer Science",
  "research_interests": ["AI", "Machine Learning"],
  "created_at": "2026-01-20T10:30:00Z",
  "updated_at": "2026-01-20T10:30:00Z"
}
```

### Paginated Response (200 OK)
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/researchers/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response (4xx/5xx)
```json
{
  "error": "Invalid request parameters",
  "detail": "Department cannot be empty."
}
```

### Graph Response (200 OK)
```json
{
  "nodes": [
    {
      "id": "researcher_1",
      "label": "Dr. Alice Smith",
      "type": "researcher",
      "cluster_id": "Computer Science",
      "data": {...}
    }
  ],
  "links": [
    {
      "source": "researcher_1",
      "target": "researcher_2",
      "type": "collaboration",
      "value": 3,
      "metadata": {...}
    }
  ],
  "summary": {...}
}
```

---

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Create database if needed
createdb daystar_db

# Run migrations
python manage.py migrate
```

### Port Already in Use
```bash
# Run on different port
python manage.py runserver 8001
```

### JWT Token Expired
```javascript
// Use refresh token to get new access token
const refreshRes = await fetch('http://localhost:8000/api/auth/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});
const { access } = await refreshRes.json();
```

---

## Support & Documentation

- **Interactive API Docs**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Backend Details**: See [BACKEND_FIXES_COMPLETE.md](BACKEND_FIXES_COMPLETE.md)
- **Frontend Guide**: See [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)

---

## License & Credits

**Project**: Daystar Research Collaboration Graph & Intelligence Hub
**Project**: Daystar Research Collaboration Graph
**Date**: January 20, 2026
**Status**: ✅ Production Ready

---

**Ready to build the frontend?** Start with the [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) for step-by-step integration instructions.
