import random
from django.core.management.base import BaseCommand
from core.models import Researcher, Project, SDG

class Command(BaseCommand):
    help = 'Seeds the database with Projects and connects Researchers to them'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Graph Data...")

        # 1. Create SDGs if they don't exist
        sdg_list = [
            (1, 'No Poverty'), (2, 'Zero Hunger'), (3, 'Good Health'), 
            (4, 'Quality Education'), (5, 'Gender Equality'), (8, 'Decent Work'),
            (9, 'Innovation'), (11, 'Sustainable Cities'), (13, 'Climate Action')
        ]
        
        sdg_objs = []
        for num, name in sdg_list:
            obj, _ = SDG.objects.get_or_create(number=num, name=name)
            sdg_objs.append(obj)

        # 2. Define the Real Projects (from your Doc)
        projects_data = [
            {
                "title": "Kibera Sanitation Intelligence (K-SISP)",
                "status": "Active",
                "year": 2024,
                "sdgs": [6, 11, 3] # Sanitation, Cities, Health
            },
            {
                "title": "Urban Citizen Sensing Platform",
                "status": "Active",
                "year": 2025,
                "sdgs": [11, 9] # Cities, Innovation
            },
            {
                "title": "Daystar Research Graph",
                "status": "Active",
                "year": 2026,
                "sdgs": [4, 9, 17] # Education, Innovation, Partnerships
            },
            {
                "title": "SDG Impact Dashboard",
                "status": "Completed",
                "year": 2024,
                "sdgs": [4, 17]
            },
            {
                "title": "Institutional Knowledge AI (DIKAI)",
                "status": "Active",
                "year": 2025,
                "sdgs": [4, 9]
            }
        ]

        researchers = list(Researcher.objects.all())
        if len(researchers) < 5:
            self.stdout.write(self.style.WARNING("Not enough researchers found! Run 'scrape_daystar' first."))
            return

        # 3. Create Projects and Assign Random Teams
        for p_data in projects_data:
            project, created = Project.objects.get_or_create(
                title=p_data['title'],
                defaults={
                    'status': p_data['status'],
                    'start_year': p_data['year']
                }
            )
            
            # Assign SDGs
            for sdg_num in p_data['sdgs']:
                sdg = SDG.objects.filter(number=sdg_num).first()
                if sdg:
                    project.sdgs.add(sdg)

            # Assign a Random "Team" of 3-6 Researchers to this project
            # This creates the EDGES in your graph!
            team_size = random.randint(3, 6)
            team = random.sample(researchers, team_size)
            
            for member in team:
                project.members.add(member)
                
                # Assign a department based on the project if 'Unassigned'
                if member.department == 'Unassigned':
                    if "Sanitation" in project.title:
                        member.department = "Public Health"
                    elif "AI" in project.title or "Graph" in project.title:
                        member.department = "Computer Science"
                    elif "Urban" in project.title:
                        member.department = "Environmental Science"
                    member.save()

            self.stdout.write(f"Created Project: {project.title} with {team_size} members.")

        self.stdout.write(self.style.SUCCESS("Graph Seeding Complete! Connections created."))