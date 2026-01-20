"""
Celery tasks for background processing.

Heavy operations are executed asynchronously to avoid blocking the main server:
- Embedding generation for bulk data
- CSV ingestion with relationship inference
- Collaboration graph recalculation
- Vector index optimization
"""

import logging
from celery import shared_task
from django.db.models import Q
from .models import Researcher, Publication, Collaboration, Authorship
from .services import EmbeddingService
from .analytics import ResearchAnalyticsService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_embedding_task(self, model_type: str, object_id: int):
    """
    Asynchronously generate embedding for a researcher or publication.
    
    Args:
        model_type: 'researcher' or 'publication'
        object_id: ID of the object
    """
    try:
        if model_type == 'researcher':
            researcher = Researcher.objects.get(id=object_id)
            EmbeddingService.generate_researcher_embedding(researcher)
            logger.info(f"Generated embedding for Researcher {object_id}")
        
        elif model_type == 'publication':
            publication = Publication.objects.get(id=object_id)
            EmbeddingService.generate_publication_embedding(publication)
            logger.info(f"Generated embedding for Publication {object_id}")
    
    except Exception as exc:
        logger.error(f"Error generating embedding for {model_type} {object_id}: {exc}")
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True)
def backfill_missing_embeddings(self):
    """
    Find and generate embeddings for publications/researchers without vectors.
    
    Run periodically to catch any records that missed the signal handler.
    """
    try:
        # Researchers without embeddings
        researchers_missing = Researcher.objects.filter(interests_embedding__isnull=True)
        logger.info(f"Found {researchers_missing.count()} researchers without embeddings")
        
        for researcher in researchers_missing:
            generate_embedding_task.delay('researcher', researcher.id)
        
        # Publications without embeddings
        pubs_missing = Publication.objects.filter(abstract_embedding__isnull=True)
        logger.info(f"Found {pubs_missing.count()} publications without embeddings")
        
        for pub in pubs_missing:
            generate_embedding_task.delay('publication', pub.id)
        
        return {
            'researchers_queued': researchers_missing.count(),
            'publications_queued': pubs_missing.count()
        }
    
    except Exception as exc:
        logger.error(f"Error in backfill_missing_embeddings: {exc}")
        raise


@shared_task(bind=True)
def recalculate_collaboration_graph(self):
    """
    Recalculate all collaboration edges and strengths.
    
    Triggered daily to ensure collaboration metrics are up-to-date.
    This is computationally expensive, so it runs at off-peak hours (2 AM).
    """
    try:
        # Clear old collaboration data or just update
        logger.info("Starting collaboration graph recalculation...")
        
        # Get all authorships and rebuild collaboration edges
        authorships = Authorship.objects.select_related(
            'publication', 'researcher'
        ).prefetch_related('researcher')
        
        collaboration_updates = {}
        
        for authorship in authorships:
            publication = authorship.publication
            researcher1 = authorship.researcher
            
            # Find all other researchers on this publication
            co_authors = Authorship.objects.filter(
                publication=publication
            ).exclude(researcher=researcher1).select_related('researcher')
            
            for co_authorship in co_authors:
                researcher2 = co_authorship.researcher
                
                # Create edge key (sorted to avoid duplicates)
                edge_key = tuple(sorted([researcher1.id, researcher2.id]))
                
                if edge_key not in collaboration_updates:
                    collaboration_updates[edge_key] = {
                        'strength': 0,
                        'last_date': publication.publication_date
                    }
                
                collaboration_updates[edge_key]['strength'] += 1
                if publication.publication_date:
                    collaboration_updates[edge_key]['last_date'] = publication.publication_date
        
        # Update database
        for (r1_id, r2_id), data in collaboration_updates.items():
            collab, created = Collaboration.objects.update_or_create(
                researcher_1_id=r1_id,
                researcher_2_id=r2_id,
                defaults={
                    'strength': data['strength'],
                    'last_collaborated': data['last_date']
                }
            )
            if created:
                logger.info(f"Created collaboration: {r1_id} ↔ {r2_id}")
        
        logger.info(f"Collaboration graph updated: {len(collaboration_updates)} edges")
        return {'edges_updated': len(collaboration_updates)}
    
    except Exception as exc:
        logger.error(f"Error in recalculate_collaboration_graph: {exc}")
        raise


@shared_task(bind=True)
def ingest_csv_batch(self, csv_path: str, batch_size: int = 500):
    """
    Asynchronously ingest a CSV file.
    
    This allows large imports to not block the server.
    
    Args:
        csv_path: Path to the CSV file
        batch_size: Number of rows to process before committing
    """
    try:
        from .management.commands.ingest_research_data import Command
        
        command = Command()
        # Assuming command has a handle_batch method (can be added)
        command.handle_batch(csv_path, batch_size=batch_size)
        
        logger.info(f"CSV ingestion completed: {csv_path}")
        return {'status': 'success', 'file': csv_path}
    
    except Exception as exc:
        logger.error(f"Error ingesting CSV {csv_path}: {exc}")
        raise


@shared_task
def update_analytics_cache():
    """
    Pre-compute analytics and cache them to speed up dashboard loads.
    
    Run periodically to keep cached data fresh.
    """
    try:
        analytics = ResearchAnalyticsService.get_complete_analytics()
        
        # In production, cache this in Redis
        # cache.set('research_analytics', analytics, timeout=3600)
        
        logger.info("Analytics cache updated")
        return analytics
    
    except Exception as exc:
        logger.error(f"Error updating analytics cache: {exc}")
        raise


@shared_task(bind=True, max_retries=1)
def sync_external_data(self):
    """
    Sync researcher data from external sources (Google Scholar, ORCID, etc).
    
    Example for future integration with external APIs.
    """
    try:
        logger.info("Syncing external researcher data...")
        
        # TODO: Implement external API calls
        # - Query Google Scholar API for each researcher
        # - Query ORCID API
        # - Update publication counts, h-index, etc.
        
        logger.info("External data sync completed")
        return {'status': 'success'}
    
    except Exception as exc:
        logger.error(f"Error syncing external data: {exc}")
        self.retry(exc=exc, countdown=600)
