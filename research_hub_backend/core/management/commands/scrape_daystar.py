import requests
import xml.etree.ElementTree as ET
import random
from django.core.management.base import BaseCommand
from core.models import Researcher

class Command(BaseCommand):
    help = 'Harvests Daystar Repository using OAI-PMH (Robust Version)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Connecting to Daystar OAI-PMH Feed...")
        
        base_url = "https://repository.daystar.ac.ke/server/oai/request"
        params = {
            "verb": "ListRecords",
            "metadataPrefix": "oai_dc"
        }

        # IGNORE LIST: Skip these non-person "authors"
        IGNORE_KEYWORDS = [
            'department', 'school', 'university', 'faculty', 'college', 
            'institute', 'center', 'centre', 'daystar', 'directorate'
        ]

        try:
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to connect: {response.status_code}"))
                return

            root = ET.fromstring(response.content)
            ns = {
                'oai': 'http://www.openarchives.org/OAI/2.0/',
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }

            records = root.findall('.//oai:record', ns)
            self.stdout.write(f"Found {len(records)} records. Processing...")

            for record in records:
                metadata = record.find('.//oai_dc:dc', ns)
                if metadata is None:
                    continue

                creators = metadata.findall('dc:creator', ns)
                
                for creator in creators:
                    raw_name = creator.text
                    if not raw_name:
                        continue
                        
                    # 1. Clean Name
                    if "," in raw_name:
                        parts = raw_name.split(",")
                        name = f"{parts[1].strip()} {parts[0].strip()}"
                    else:
                        name = raw_name.strip()

                    # 2. FILTER: Skip Departments/Institutions
                    if any(word in name.lower() for word in IGNORE_KEYWORDS):
                        continue
                    
                    # 3. FILTER: Skip very short names (likely data errors)
                    if len(name) < 4:
                        continue

                    # 4. Generate Unique Email (Fixes the Crash)
                    # We generate a slug. If that slug is taken by SOMEONE ELSE, we append numbers.
                    slug = name.replace(' ', '.').replace(',', '').replace("'", "").lower()
                    email = f"{slug}@daystar.ac.ke"
                    
                    # Check if email exists for a DIFFERENT name
                    if Researcher.objects.filter(email=email).exclude(name=name).exists():
                        email = f"{slug}.{random.randint(100, 999)}@daystar.ac.ke"

                    # 5. Save to DB
                    researcher, created = Researcher.objects.get_or_create(
                        name=name,
                        defaults={
                            'department': 'Unassigned',
                            'email': email
                        }
                    )
                    
                    researcher.publications_count += 1
                    researcher.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added: {name}"))

            self.stdout.write(self.style.SUCCESS(f"Done!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))