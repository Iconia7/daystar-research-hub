from django.core.management.base import BaseCommand
from core.models import Researcher
from scholarly import scholarly

class Command(BaseCommand):
    help = 'Enriches researcher profiles using Google Scholar data'

    def handle(self, *args, **kwargs):
        researchers = Researcher.objects.all()

        self.stdout.write(f"Enriching {researchers.count()} profiles...")

        for researcher in researchers:
            try:
                self.stdout.write(f"Searching Scholar for: {researcher.name}...")
                
                # 1. SEARCH GOOGLE SCHOLAR
                search_query = scholarly.search_author(researcher.name)
                author = next(search_query, None) # Get first result

                if author:
                    # 2. FILL DETAILS
                    # We must 'fill' the author object to get stats
                    author = scholarly.fill(author, sections=['indices', 'counts'])
                    
                    # Update Django Model
                    researcher.h_index = author.get('hindex', 0)
                    researcher.citations = author.get('citedby', 0)
                    
                    # Extract tags/interests if available
                    interests = author.get('interests', [])
                    if interests:
                        researcher.tags = ", ".join(interests) # Save as "AI, Data Science"
                    
                    # Try to guess department from affiliation if missing
                    if researcher.department == 'Unassigned' and 'affiliation' in author:
                        if 'Computer' in author['affiliation']:
                            researcher.department = 'Computer Science'
                        elif 'Health' in author['affiliation']:
                            researcher.department = 'Public Health'
                        elif 'Economics' in author['affiliation']:
                            researcher.department = 'Economics'

                    researcher.save()
                    self.stdout.write(self.style.SUCCESS(f"UPDATED: {researcher.name} (H-Index: {researcher.h_index})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Not found on Scholar: {researcher.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {researcher.name}: {e}"))