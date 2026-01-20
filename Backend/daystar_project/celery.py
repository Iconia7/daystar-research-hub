"""
Celery configuration for Daystar Research Collaboration Graph.

This module configures Celery to handle background tasks like:
- Embedding generation
- Batch CSV ingestion
- Collaboration graph recalculation
- Vector index updates
"""

import os
from celery import Celery
from celery.schedules import crontab # type: ignore

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daystar_project.settings')

# Create Celery instance
app = Celery('daystar_project')

# Load configuration from Django settings (all keys in settings.py starting with CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Schedule (periodic tasks)
app.conf.beat_schedule = {
    'recalculate-collaboration-graph': {
        'task': 'research_graph.tasks.recalculate_collaboration_graph',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'backfill-missing-embeddings': {
        'task': 'research_graph.tasks.backfill_missing_embeddings',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
