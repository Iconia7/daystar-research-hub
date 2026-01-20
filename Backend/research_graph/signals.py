"""
Signal handlers for automatic embedding generation.
Triggered when Researcher or Publication objects are saved.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import numpy as np
from .models import Researcher, Publication
from .services import EmbeddingService

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Researcher)
def generate_researcher_embedding(sender, instance, **kwargs):
    """
    Signal handler that generates embeddings for Researcher research interests.
    
    Triggered before saving a Researcher instance. Converts research interests
    into a semantic vector using the embedding service.
    """
    try:
        # Only generate embedding if research interests are provided
        if instance.research_interests and instance.research_interests != []:
            # Join research interests into a single text
            interests_text = " ".join(instance.research_interests)
            
            # Generate embedding
            embedding = EmbeddingService.get_embedding(interests_text)
            
            if embedding is not None:
                # Convert to numpy array and store as vector
                instance.interests_embedding = embedding
                logger.info(
                    f"Generated embedding for Researcher: {instance.user.get_full_name()}"
                )
            else:
                logger.warning(
                    f"Failed to generate embedding for Researcher: {instance.user.get_full_name()}"
                )
        else:
            # Clear embedding if no interests provided
            instance.interests_embedding = None
            
    except Exception as e:
        logger.error(f"Error generating Researcher embedding: {str(e)}")
        # Don't raise - let the save continue even if embedding fails
        pass


@receiver(pre_save, sender=Publication)
def generate_publication_embedding(sender, instance, **kwargs):
    """
    Signal handler that generates embeddings for Publication abstracts.
    
    Triggered before saving a Publication instance. Converts the abstract
    into a semantic vector using the embedding service.
    """
    try:
        # Only generate embedding if abstract is provided
        if instance.abstract and instance.abstract.strip():
            # Generate embedding from abstract
            embedding = EmbeddingService.get_embedding(instance.abstract)
            
            if embedding is not None:
                # Convert to numpy array and store as vector
                instance.abstract_embedding = embedding
                logger.info(
                    f"Generated embedding for Publication: {instance.title[:50]}"
                )
            else:
                logger.warning(
                    f"Failed to generate embedding for Publication: {instance.title[:50]}"
                )
        else:
            # Clear embedding if no abstract provided
            instance.abstract_embedding = None
            
    except Exception as e:
        logger.error(f"Error generating Publication embedding: {str(e)}")
        # Don't raise - let the save continue even if embedding fails
        pass
