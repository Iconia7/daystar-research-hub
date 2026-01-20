"""
Management command to ingest research data from CSV file.

Usage:
    python manage.py ingest_research_data path/to/data.csv
    python manage.py ingest_research_data --help

CSV Format:
    Title,Authors,Abstract,Year,Department
    "Deep Learning for...",Alice Smith;Bob Jones,Abstract text...,2024,Computer Science
    ...

Features:
- Creates or updates Publications
- Creates or updates Researchers
- Creates Authorship relationships with author order
- Creates Collaboration edges and updates strength
"""
import csv
import logging
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from research_graph.models import (
    Researcher, Publication, Authorship, Collaboration
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ingest research data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing research data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse CSV and show what would be imported without saving'
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='Continue on errors instead of stopping'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process before committing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        skip_errors = options['skip_errors']
        batch_size = options['batch_size']

        # Validate file
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

        self.stdout.write(self.style.SUCCESS(f'\n📂 Loading CSV: {csv_file}'))

        # Parse and process
        try:
            stats = self.process_csv(csv_file, dry_run, skip_errors, batch_size)
            self.display_stats(stats)
        except Exception as e:
            if not skip_errors:
                raise CommandError(f'Fatal error: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def process_csv(self, csv_file, dry_run, skip_errors, batch_size):
        """Process CSV file and return statistics."""
        
        stats = {
            'rows_processed': 0,
            'publications_created': 0,
            'publications_updated': 0,
            'researchers_created': 0,
            'authorships_created': 0,
            'collaborations_created': 0,
            'errors': []
        }

        with transaction.atomic():
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Validate headers
                required_fields = {'Title', 'Authors', 'Abstract', 'Year', 'Department'}
                if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
                    raise CommandError(
                        f'CSV must have columns: {", ".join(required_fields)}'
                    )

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    try:
                        self.process_row(row, stats)
                        
                        # Batch commit
                        if stats['rows_processed'] % batch_size == 0:
                            self.stdout.write(
                                f"  ✓ Processed {stats['rows_processed']} rows..."
                            )
                    
                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        stats['errors'].append(error_msg)
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ {error_msg}")
                        )
                        
                        if not skip_errors:
                            raise
                    
                    finally:
                        stats['rows_processed'] += 1

        return stats

    def process_row(self, row, stats):
        """
        Process a single CSV row.
        
        Steps:
        1. Create/get Publication
        2. For each author:
           a. Create/get Researcher
           b. Create Authorship
           c. Track author for collaborations
        3. Create Collaborations between co-authors
        """
        
        # Extract fields
        title = row.get('Title', '').strip()
        authors_str = row.get('Authors', '').strip()
        abstract = row.get('Abstract', '').strip()
        year_str = row.get('Year', '').strip()
        department = row.get('Department', '').strip()

        # Validate required fields
        if not title:
            raise ValueError("Title is required")
        if not authors_str:
            raise ValueError("Authors is required")
        if not year_str:
            raise ValueError("Year is required")

        # Parse year
        try:
            year = int(year_str)
            publication_date = date(year, 1, 1)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid year: {year_str}")

        # Parse authors (comma or semicolon separated)
        author_names = [n.strip() for n in authors_str.replace(';', ',').split(',')]
        author_names = [n for n in author_names if n]  # Remove empty

        if not author_names:
            raise ValueError("No valid authors found")

        # ==================== Create/Get Publication ====================

        publication, created = Publication.objects.get_or_create(
            title=title,
            defaults={
                'abstract': abstract,
                'publication_date': publication_date,
            }
        )

        if created:
            stats['publications_created'] += 1
            self.stdout.write(f"  + Created publication: {title[:50]}...")
        else:
            stats['publications_updated'] += 1

        # ==================== Create/Get Researchers & Authorships ====================

        researchers = []
        
        for order, author_name in enumerate(author_names, start=1):
            # Parse name (assume "FirstName LastName" format)
            name_parts = author_name.rsplit(' ', 1)
            if len(name_parts) == 2:
                first_name, last_name = name_parts
            else:
                first_name = author_name
                last_name = ''

            # Get or create User
            user, user_created = User.objects.get_or_create(
                username=self._generate_username(first_name, last_name),
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            # Get or create Researcher
            researcher, res_created = Researcher.objects.get_or_create(
                user=user,
                defaults={
                    'department': department,
                }
            )

            if res_created:
                stats['researchers_created'] += 1
                self.stdout.write(f"    + Created researcher: {author_name}")

            # Create Authorship
            authorship, auth_created = Authorship.objects.get_or_create(
                researcher=researcher,
                publication=publication,
                defaults={'order': order}
            )

            if auth_created:
                stats['authorships_created'] += 1

            researchers.append(researcher)

        # ==================== Create Collaborations ====================

        # Create collaboration edges between all co-authors
        for i, researcher_1 in enumerate(researchers):
            for researcher_2 in researchers[i + 1:]:
                # Ensure consistent edge direction (lower ID first)
                if researcher_1.id > researcher_2.id:
                    researcher_1, researcher_2 = researcher_2, researcher_1

                # Get or create collaboration
                collab, collab_created = Collaboration.objects.get_or_create(
                    researcher_1=researcher_1,
                    researcher_2=researcher_2,
                    defaults={
                        'strength': 1,
                        'last_collaborated': publication_date,
                    }
                )

                if collab_created:
                    stats['collaborations_created'] += 1
                else:
                    # Update existing: increment strength and update date
                    collab.strength += 1
                    if not collab.last_collaborated or publication_date > collab.last_collaborated:
                        collab.last_collaborated = publication_date
                    collab.save()

    @staticmethod
    def _generate_username(first_name, last_name):
        """
        Generate a unique username from first and last names.
        
        Format: firstname_lastname (lowercase)
        If exists, append number: firstname_lastname_2, etc.
        """
        base_username = f"{first_name.lower()}_{last_name.lower()}".replace(' ', '_')
        username = base_username
        counter = 2

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    def display_stats(self, stats):
        """Display ingestion statistics."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 INGESTION STATISTICS')
        self.stdout.write('=' * 70)

        self.stdout.write(f"\n✓ Rows processed: {stats['rows_processed']}")
        self.stdout.write(f"✓ Publications created: {stats['publications_created']}")
        self.stdout.write(f"✓ Publications updated: {stats['publications_updated']}")
        self.stdout.write(f"✓ Researchers created: {stats['researchers_created']}")
        self.stdout.write(f"✓ Authorships created: {stats['authorships_created']}")
        self.stdout.write(f"✓ Collaborations created: {stats['collaborations_created']}")

        if stats['errors']:
            self.stdout.write(f"\n⚠ Errors: {len(stats['errors'])}")
            for error in stats['errors'][:10]:  # Show first 10 errors
                self.stdout.write(self.style.ERROR(f"  - {error}"))
            if len(stats['errors']) > 10:
                self.stdout.write(f"  ... and {len(stats['errors']) - 10} more")

        self.stdout.write('\n' + '=' * 70 + '\n')
