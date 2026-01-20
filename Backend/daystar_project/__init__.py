"""
Daystar Research Collaboration Graph project.

This module initializes Celery for background task processing.
"""

# Import Celery app at module startup to ensure tasks are registered
from .celery import app as celery_app

__all__ = ('celery_app',)
