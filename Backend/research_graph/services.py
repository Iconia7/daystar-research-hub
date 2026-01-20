"""
Services for semantic search, embeddings, and intelligent matching.

This module provides:
- Embedding generation (using sentence-transformers for local embeddings)
- Semantic similarity matching
- Supervisor matching based on thesis topics
- Grant alignment with researcher interests
"""
import logging
from typing import List, Optional, Tuple
import numpy as np
from django.db.models import F, Case, When, DecimalField
from django.contrib.postgres.search import TrigramSimilarity
from pgvector.django import L2Distance, CosineDistance
from .models import Researcher, Publication, Thesis

logger = logging.getLogger(__name__)

# Lazy load sentence transformers to avoid startup delay
_embedding_model = None

def get_embedding_model():
    """Lazy load embedding model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            _embedding_model = False  # Mark as failed
    return _embedding_model if _embedding_model is not False else None


class EmbeddingService:
    """
    Service for generating and managing vector embeddings.
    
    Uses sentence-transformers for local embeddings (no API keys required).
    Can be easily switched to OpenAI or other providers.
    """
    
    EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 produces 384-dim embeddings
    
    @staticmethod
    def get_embedding(text: str) -> Optional[List[float]]:
        """
        Generate a vector embedding for the given text.
        
        Uses sentence-transformers library for local embedding generation.
        Falls back to random vectors if model is unavailable.
        
        Args:
            text: The text to embed (researcher interests, publication abstract, etc.)
            
        Returns:
            List of floats representing the embedding, or None if generation fails.
        """
        if not text or not text.strip():
            return None
        
        try:
            model = get_embedding_model()
            
            if model:
                # Use sentence transformers
                embedding = model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                # Fallback: generate deterministic random vector
                np.random.seed(hash(text) % (2**32))
                embedding = np.random.randn(EmbeddingService.EMBEDDING_DIMENSION).astype(float)
                embedding = embedding / np.linalg.norm(embedding)
                logger.warning(f"Using fallback embedding for text: {text[:50]}...")
                return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    @staticmethod
    def batch_embed_researchers() -> None:
        """
        Generate embeddings for all researchers lacking them.
        
        Useful for backfilling embeddings after adding VectorField to existing database.
        """
        researchers = Researcher.objects.filter(interests_embedding__isnull=True)
        count = 0
        
        for researcher in researchers:
            if researcher.research_interests:
                interests_text = " ".join(researcher.research_interests)
                embedding = EmbeddingService.get_embedding(interests_text)
                if embedding:
                    researcher.interests_embedding = embedding
                    researcher.save(update_fields=['interests_embedding'])
                    count += 1
        
        logger.info(f"Generated embeddings for {count} researchers")
    
    @staticmethod
    def batch_embed_publications() -> None:
        """
        Generate embeddings for all publications lacking them.
        
        Useful for backfilling embeddings after adding VectorField to existing database.
        """
        publications = Publication.objects.filter(abstract_embedding__isnull=True)
        count = 0
        
        for publication in publications:
            if publication.abstract:
                embedding = EmbeddingService.get_embedding(publication.abstract)
                if embedding:
                    publication.abstract_embedding = embedding
                    publication.save(update_fields=['abstract_embedding'])
                    count += 1
        
        logger.info(f"Generated embeddings for {count} publications")


class SupervisorMatchingService:
    """
    Service for intelligent supervisor matching based on semantic similarity.
    
    Uses vector embeddings to match thesis topics with researcher expertise,
    enabling matching even when keywords don't align exactly.
    """
    
    @staticmethod
    def find_supervisor_match(
        thesis_abstract: str,
        department: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[Researcher, float]]:
        """
        Find the best supervisor matches for a thesis topic.
        
        Uses cosine similarity between the thesis abstract embedding and
        researcher interest embeddings to find the most suitable supervisors.
        
        Args:
            thesis_abstract: The thesis abstract to match
            department: Optional department filter (e.g., "Computer Science")
            top_k: Number of top matches to return (default: 5)
            
        Returns:
            List of tuples (Researcher, similarity_score) sorted by similarity
            in descending order. Similarity scores range from 0 to 1.
            
        Example:
            >>> abstract = "Deep learning models for climate prediction"
            >>> matches = SupervisorMatchingService.find_supervisor_match(abstract)
            >>> for researcher, score in matches:
            ...     print(f"{researcher.user.get_full_name()}: {score:.4f}")
        """
        try:
            # Generate embedding for the thesis abstract
            thesis_embedding = EmbeddingService.get_embedding(thesis_abstract)
            
            if thesis_embedding is None:
                logger.warning("Failed to generate embedding for thesis abstract")
                return []
            
            # Query researchers with embeddings, using cosine distance
            query = Researcher.objects.filter(
                interests_embedding__isnull=False
            ).annotate(
                similarity=CosineDistance('interests_embedding', thesis_embedding)
            ).order_by('similarity')  # Lower distance = higher similarity
            
            # Apply department filter if provided
            if department:
                query = query.filter(department=department)
            
            # Extract results with similarity scores (convert distance to similarity)
            # Cosine distance is [0, 2], so similarity = 1 - (distance / 2)
            results = []
            for researcher in query[:top_k]:
                # Convert cosine distance to similarity score (0-1)
                similarity_score = 1 - (researcher.similarity / 2)
                results.append((researcher, float(similarity_score)))
            
            logger.info(
                f"Found {len(results)} supervisor matches for thesis abstract"
            )
            return results
            
        except Exception as e:
            logger.error(f"Error finding supervisor matches: {str(e)}")
            return []
    
    @staticmethod
    def find_thesis_matches(
        researcher: Researcher,
        top_k: int = 5
    ) -> List[Tuple[Publication, float]]:
        """
        Find publications similar to a researcher's interests.
        
        Uses cosine similarity between researcher interest embeddings and
        publication abstract embeddings to suggest relevant research.
        
        Args:
            researcher: The researcher to match
            top_k: Number of top matches to return (default: 5)
            
        Returns:
            List of tuples (Publication, similarity_score) sorted by similarity
            
        Example:
            >>> researcher = Researcher.objects.first()
            >>> matches = SupervisorMatchingService.find_thesis_matches(researcher)
        """
        try:
            if not researcher.interests_embedding:
                logger.warning(f"Researcher {researcher.id} has no embedding")
                return []
            
            # Query publications with embeddings, using cosine distance
            query = Publication.objects.filter(
                abstract_embedding__isnull=False
            ).annotate(
                similarity=CosineDistance('abstract_embedding', researcher.interests_embedding)
            ).order_by('similarity')
            
            # Extract results with similarity scores
            results = []
            for publication in query[:top_k]:
                similarity_score = 1 - (publication.similarity / 2)
                results.append((publication, float(similarity_score)))
            
            logger.info(
                f"Found {len(results)} publications matching researcher interests"
            )
            return results
            
        except Exception as e:
            logger.error(f"Error finding publication matches: {str(e)}")
            return []


class GrantAlignmentService:
    """
    Service for aligning research projects/grants with researcher expertise.
    
    Helps match grant opportunities with researchers based on semantic similarity
    of research interests and grant objectives.
    """
    
    @staticmethod
    def find_aligned_researchers(
        grant_description: str,
        department: Optional[str] = None,
        top_k: int = 10
    ) -> List[Tuple[Researcher, float]]:
        """
        Find researchers whose expertise aligns with grant objectives.
        
        Args:
            grant_description: Description of the grant or project
            department: Optional department filter
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (Researcher, alignment_score) sorted by alignment
            
        Example:
            >>> grant = "AI applications in healthcare and medical imaging"
            >>> matches = GrantAlignmentService.find_aligned_researchers(grant)
        """
        try:
            # Generate embedding for grant description
            grant_embedding = EmbeddingService.get_embedding(grant_description)
            
            if grant_embedding is None:
                logger.warning("Failed to generate embedding for grant description")
                return []
            
            # Query researchers
            query = Researcher.objects.filter(
                interests_embedding__isnull=False
            ).annotate(
                alignment=CosineDistance('interests_embedding', grant_embedding)
            ).order_by('alignment')
            
            if department:
                query = query.filter(department=department)
            
            # Extract results
            results = []
            for researcher in query[:top_k]:
                alignment_score = 1 - (researcher.alignment / 2)
                results.append((researcher, float(alignment_score)))
            
            logger.info(f"Found {len(results)} researchers aligned with grant")
            return results
            
        except Exception as e:
            logger.error(f"Error finding aligned researchers: {str(e)}")
            return []
    
    @staticmethod
    def score_researcher_for_grant(
        researcher: Researcher,
        grant_description: str
    ) -> float:
        """
        Calculate alignment score for a specific researcher-grant pair.
        
        Args:
            researcher: The researcher to score
            grant_description: The grant or project description
            
        Returns:
            Alignment score from 0 to 1, where 1 is perfect alignment
            
        Example:
            >>> researcher = Researcher.objects.first()
            >>> score = GrantAlignmentService.score_researcher_for_grant(
            ...     researcher, "AI and climate change research"
            ... )
        """
        try:
            if not researcher.interests_embedding:
                return 0.0
            
            grant_embedding = EmbeddingService.get_embedding(grant_description)
            if grant_embedding is None:
                return 0.0
            
            # Calculate cosine distance
            grant_vector = np.array(grant_embedding)
            researcher_vector = np.array(researcher.interests_embedding)
            
            # Cosine similarity = 1 - distance/2
            distance = CosineDistance()._output_field.get_default()
            # Manual calculation for single pair
            from scipy.spatial.distance import cosine # type: ignore
            try:
                distance_value = cosine(researcher_vector, grant_vector)
                similarity = 1 - (distance_value / 2) if distance_value <= 2 else 0
            except:
                similarity = 0.0
            
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Error scoring researcher-grant alignment: {str(e)}")
            return 0.0
