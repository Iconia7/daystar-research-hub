"""
Management command to test and demonstrate Phase 2 matching services.

Usage:
    python manage.py test_vector_search --type=supervisor --query="thesis abstract here"
    python manage.py test_vector_search --type=grant --query="grant description here"
    python manage.py test_vector_search --type=backfill
"""
from django.core.management.base import BaseCommand, CommandError
from research_graph.models import Researcher, Publication
from research_graph.services import (
    EmbeddingService,
    SupervisorMatchingService,
    GrantAlignmentService
)


class Command(BaseCommand):
    help = 'Test and demonstrate vector search and matching services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='supervisor',
            help='Type of matching: supervisor, grant, or backfill'
        )
        parser.add_argument(
            '--query',
            type=str,
            default=None,
            help='Query text for supervisor or grant matching'
        )
        parser.add_argument(
            '--researcher',
            type=int,
            default=None,
            help='Researcher ID for testing publication matches'
        )
        parser.add_argument(
            '--top-k',
            type=int,
            default=5,
            help='Number of top matches to return'
        )
        parser.add_argument(
            '--department',
            type=str,
            default=None,
            help='Filter by department'
        )

    def handle(self, *args, **options):
        match_type = options['type'].lower()
        
        if match_type == 'supervisor':
            self.test_supervisor_matching(options)
        elif match_type == 'grant':
            self.test_grant_alignment(options)
        elif match_type == 'backfill':
            self.test_backfill(options)
        else:
            raise CommandError(f"Unknown type: {match_type}")
    
    def test_supervisor_matching(self, options):
        """Test supervisor matching service."""
        self.stdout.write(self.style.SUCCESS('\n=== Testing Supervisor Matching ===\n'))
        
        query = options['query']
        if not query:
            # Use default thesis abstract
            query = """
            Deep Learning Architectures for Climate Prediction
            
            This thesis investigates novel deep learning architectures,
            particularly attention mechanisms and transformer models,
            for predicting climate patterns and extreme weather events.
            """
            self.stdout.write(self.style.WARNING('Using default thesis abstract'))
        
        self.stdout.write(f'Query: {query[:100]}...\n')
        
        # Get matches
        matches = SupervisorMatchingService.find_supervisor_match(
            thesis_abstract=query,
            department=options['department'],
            top_k=options['top_k']
        )
        
        if not matches:
            self.stdout.write(self.style.WARNING('No matches found. Try adding researchers first.'))
            return
        
        # Display results
        self.stdout.write(self.style.SUCCESS(f'Found {len(matches)} supervisor matches:\n'))
        self.stdout.write(f"{'Rank':<6} {'Researcher':<30} {'Similarity':<12} {'Department'}")
        self.stdout.write('-' * 70)
        
        for i, (researcher, score) in enumerate(matches, 1):
            dept = researcher.department or 'N/A'
            self.stdout.write(
                f"{i:<6} {researcher.user.get_full_name():<30} {score:.4f}       {dept}"
            )
        
        self.stdout.write()
    
    def test_grant_alignment(self, options):
        """Test grant alignment service."""
        self.stdout.write(self.style.SUCCESS('\n=== Testing Grant Alignment ===\n'))
        
        query = options['query']
        if not query:
            # Use default grant description
            query = """
            NSF SBIR Phase II: AI for Sustainable Energy Systems
            
            This grant supports innovative research into machine learning
            and deep learning applications for renewable energy optimization,
            smart grid management, and climate prediction systems.
            """
            self.stdout.write(self.style.WARNING('Using default grant description'))
        
        self.stdout.write(f'Query: {query[:100]}...\n')
        
        # Get matches
        matches = GrantAlignmentService.find_aligned_researchers(
            grant_description=query,
            department=options['department'],
            top_k=options['top_k']
        )
        
        if not matches:
            self.stdout.write(self.style.WARNING('No matches found. Try adding researchers first.'))
            return
        
        # Display results
        self.stdout.write(self.style.SUCCESS(f'Found {len(matches)} aligned researchers:\n'))
        self.stdout.write(f"{'Rank':<6} {'Researcher':<30} {'Alignment':<12} {'Department'}")
        self.stdout.write('-' * 70)
        
        for i, (researcher, score) in enumerate(matches, 1):
            dept = researcher.department or 'N/A'
            self.stdout.write(
                f"{i:<6} {researcher.user.get_full_name():<30} {score:.4f}       {dept}"
            )
        
        self.stdout.write()
    
    def test_backfill(self, options):
        """Backfill embeddings for existing data."""
        self.stdout.write(self.style.SUCCESS('\n=== Backfilling Embeddings ===\n'))
        
        # Count current status
        researchers_total = Researcher.objects.count()
        researchers_with_embed = Researcher.objects.filter(
            interests_embedding__isnull=False
        ).count()
        
        publications_total = Publication.objects.count()
        publications_with_embed = Publication.objects.filter(
            abstract_embedding__isnull=False
        ).count()
        
        self.stdout.write(f'Researchers: {researchers_with_embed}/{researchers_total} with embeddings')
        self.stdout.write(f'Publications: {publications_with_embed}/{publications_total} with embeddings\n')
        
        # Backfill researchers
        if researchers_with_embed < researchers_total:
            self.stdout.write('Generating researcher embeddings...')
            EmbeddingService.batch_embed_researchers()
            self.stdout.write(self.style.SUCCESS('✓ Researchers done'))
        
        # Backfill publications
        if publications_with_embed < publications_total:
            self.stdout.write('Generating publication embeddings...')
            EmbeddingService.batch_embed_publications()
            self.stdout.write(self.style.SUCCESS('✓ Publications done'))
        
        # Show final status
        researchers_with_embed = Researcher.objects.filter(
            interests_embedding__isnull=False
        ).count()
        publications_with_embed = Publication.objects.filter(
            abstract_embedding__isnull=False
        ).count()
        
        self.stdout.write(f'\nFinal status:')
        self.stdout.write(f'Researchers: {researchers_with_embed}/{researchers_total} with embeddings')
        self.stdout.write(f'Publications: {publications_with_embed}/{publications_total} with embeddings\n')
