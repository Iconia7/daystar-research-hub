"""
Phase 2 Testing Examples - Vector Search & Semantic Matching

This script demonstrates how to use the new Phase 2 features:
- Automatic embedding generation
- Supervisor matching
- Grant alignment
- Publication recommendations

Run with:
    python manage.py shell
    exec(open('phase2_examples.py').read())
"""

from django.contrib.auth.models import User
from research_graph.models import Researcher, Publication, Thesis
from research_graph.services import (
    EmbeddingService,
    SupervisorMatchingService,
    GrantAlignmentService
)


def create_sample_researchers():
    """Create sample researchers with diverse interests."""
    print("=" * 70)
    print("CREATING SAMPLE RESEARCHERS")
    print("=" * 70)
    
    researchers_data = [
        {
            'username': 'dr_alice_ml',
            'first_name': 'Alice',
            'last_name': 'Chen',
            'department': 'Computer Science',
            'interests': ['Machine Learning', 'Deep Learning', 'Computer Vision', 'Neural Networks'],
        },
        {
            'username': 'dr_bob_climate',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'department': 'Environmental Science',
            'interests': ['Climate Modeling', 'Environmental Prediction', 'Time Series Analysis', 'Sustainability'],
        },
        {
            'username': 'dr_carol_quantum',
            'first_name': 'Carol',
            'last_name': 'Johnson',
            'department': 'Physics',
            'interests': ['Quantum Computing', 'Quantum Error Correction', 'Quantum Algorithms', 'NISQ'],
        },
        {
            'username': 'dr_david_nlp',
            'first_name': 'David',
            'last_name': 'Williams',
            'department': 'Computer Science',
            'interests': ['Natural Language Processing', 'Text Analysis', 'Transformers', 'Language Models'],
        },
        {
            'username': 'dr_emma_energy',
            'first_name': 'Emma',
            'last_name': 'Davis',
            'department': 'Engineering',
            'interests': ['Renewable Energy', 'Smart Grid', 'Energy Optimization', 'Sustainable Development'],
        },
    ]
    
    researchers = []
    for data in researchers_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
            }
        )
        
        researcher, created = Researcher.objects.get_or_create(
            user=user,
            defaults={
                'department': data['department'],
                'research_interests': data['interests'],
            }
        )
        
        researchers.append(researcher)
        status = "✓ Created" if created else "→ Exists"
        print(f"{status}: {researcher.user.get_full_name()}")
        print(f"  Department: {researcher.department}")
        print(f"  Interests: {', '.join(researcher.research_interests)}")
        print(f"  Embedding: {'✓ Generated' if researcher.interests_embedding else '✗ Not generated'}")
        print()
    
    return researchers


def test_supervisor_matching():
    """Test finding the best supervisor for a thesis."""
    print("\n" + "=" * 70)
    print("TEST 1: SUPERVISOR MATCHING")
    print("=" * 70 + "\n")
    
    # Thesis abstract
    thesis_abstract = """
    Hybrid Deep Learning Models for Climate and Weather Prediction
    
    This thesis proposes innovative deep learning architectures that combine
    convolutional neural networks and recurrent networks for predicting
    weather patterns and climate trends. We employ attention mechanisms
    and transfer learning to improve prediction accuracy on limited datasets.
    """
    
    print(f"Thesis: {thesis_abstract[:100]}...\n")
    
    # Find matches
    matches = SupervisorMatchingService.find_supervisor_match(
        thesis_abstract=thesis_abstract,
        top_k=5
    )
    
    if matches:
        print("Top Supervisor Matches:")
        print(f"{'Rank':<6} {'Researcher':<25} {'Similarity':<12} {'Department'}")
        print("-" * 70)
        
        for i, (researcher, score) in enumerate(matches, 1):
            print(
                f"{i:<6} {researcher.user.get_full_name():<25} {score:.4f}       {researcher.department}"
            )
    else:
        print("⚠ No matches found (embeddings may not be generated)")
    
    return matches


def test_grant_alignment():
    """Test finding researchers aligned with a grant."""
    print("\n" + "=" * 70)
    print("TEST 2: GRANT ALIGNMENT")
    print("=" * 70 + "\n")
    
    grant_description = """
    NSF Award: AI and Machine Learning for Sustainable Development Goals
    
    This grant supports cutting-edge research combining artificial intelligence,
    machine learning, and deep learning with sustainable energy systems,
    climate prediction, and environmental monitoring. Priority areas include
    renewable energy optimization, smart grid management, and climate analytics.
    """
    
    print(f"Grant: {grant_description[:100]}...\n")
    
    # Find aligned researchers
    matches = GrantAlignmentService.find_aligned_researchers(
        grant_description=grant_description,
        top_k=5
    )
    
    if matches:
        print("Most Aligned Researchers:")
        print(f"{'Rank':<6} {'Researcher':<25} {'Alignment':<12} {'Department'}")
        print("-" * 70)
        
        for i, (researcher, score) in enumerate(matches, 1):
            print(
                f"{i:<6} {researcher.user.get_full_name():<25} {score:.4f}       {researcher.department}"
            )
    else:
        print("⚠ No matches found (embeddings may not be generated)")
    
    return matches


def test_publication_recommendations():
    """Test finding publications relevant to a researcher."""
    print("\n" + "=" * 70)
    print("TEST 3: PUBLICATION RECOMMENDATIONS")
    print("=" * 70 + "\n")
    
    # Get a researcher
    try:
        researcher = Researcher.objects.filter(
            interests_embedding__isnull=False
        ).first()
        
        if not researcher:
            print("⚠ No researchers with embeddings found")
            return
        
        print(f"Researcher: {researcher.user.get_full_name()}")
        print(f"Department: {researcher.department}")
        print(f"Interests: {', '.join(researcher.research_interests)}\n")
        
        # Find similar publications
        matches = SupervisorMatchingService.find_thesis_matches(
            researcher=researcher,
            top_k=5
        )
        
        if matches:
            print("Recommended Publications:")
            print(f"{'Rank':<6} {'Title':<40} {'Similarity':<12}")
            print("-" * 70)
            
            for i, (pub, score) in enumerate(matches, 1):
                title = (pub.title[:37] + "...") if len(pub.title) > 40 else pub.title
                print(f"{i:<6} {title:<40} {score:.4f}")
        else:
            print("⚠ No publications with embeddings found")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_embedding_generation():
    """Test automatic embedding generation."""
    print("\n" + "=" * 70)
    print("TEST 4: EMBEDDING GENERATION")
    print("=" * 70 + "\n")
    
    # Create a new researcher to test signal
    user = User.objects.create_user(
        username='test_embed',
        first_name='Test',
        last_name='Embedding'
    )
    
    researcher = Researcher.objects.create(
        user=user,
        department='Test Department',
        research_interests=['Signal Testing', 'Embedding Generation', 'Auto Trigger']
    )
    
    print(f"Created: {researcher.user.get_full_name()}")
    print(f"Interests: {researcher.research_interests}")
    
    # Check if embedding was generated
    if researcher.interests_embedding:
        embedding_vec = researcher.interests_embedding
        print(f"✓ Embedding generated successfully!")
        print(f"  Dimension: {len(embedding_vec)}")
        print(f"  Sample values: {embedding_vec[:3]}")
    else:
        print("✗ Embedding not generated (signals may not be registered)")


def show_embedding_stats():
    """Show statistics about embeddings."""
    print("\n" + "=" * 70)
    print("EMBEDDING STATISTICS")
    print("=" * 70 + "\n")
    
    researchers_total = Researcher.objects.count()
    researchers_with_embed = Researcher.objects.filter(
        interests_embedding__isnull=False
    ).count()
    
    publications_total = Publication.objects.count()
    publications_with_embed = Publication.objects.filter(
        abstract_embedding__isnull=False
    ).count()
    
    print(f"Researchers:")
    print(f"  Total: {researchers_total}")
    print(f"  With embeddings: {researchers_with_embed}")
    print(f"  Coverage: {100*researchers_with_embed//researchers_total}%")
    
    print(f"\nPublications:")
    print(f"  Total: {publications_total}")
    print(f"  With embeddings: {publications_with_embed}")
    if publications_total > 0:
        print(f"  Coverage: {100*publications_with_embed//publications_total}%")
    else:
        print(f"  Coverage: N/A (no publications)")


def main():
    """Run all Phase 2 tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PHASE 2: VECTOR SEARCH DEMONSTRATION" + " " * 17 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Show current stats
    show_embedding_stats()
    
    # Create sample data if needed
    researchers_count = Researcher.objects.count()
    if researchers_count == 0:
        print("\nNo researchers found. Creating sample data...")
        create_sample_researchers()
    else:
        print(f"\n✓ Found {researchers_count} existing researchers")
    
    # Run tests
    try:
        test_supervisor_matching()
        test_grant_alignment()
        test_publication_recommendations()
        test_embedding_generation()
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Final stats
    show_embedding_stats()
    
    print("\n" + "=" * 70)
    print("PHASE 2 TESTING COMPLETE")
    print("=" * 70 + "\n")


# Run all tests
if __name__ == '__main__':
    main()
