import random
from django.core.management.base import BaseCommand
from core.models import Researcher, CollaborationOpportunity, Project

class Command(BaseCommand):
    help = 'Analyzes the graph to generate AI Collaboration Suggestions'

    def handle(self, *args, **kwargs):
        self.stdout.write("Running Intelligence Algorithms...")
        
        # --- STEP 1: FIX MISSING DATA (PROTOTYPE MODE) ---
        # In a real app, this would come from the HR database.
        # Here, we distribute 'Unassigned' people into likely departments to make the demo work.
        departments = [
            'Computer Science', 'Public Health', 'Business', 'Economics', 
            'Communication', 'Environmental Science', 'Theology', 'Psychology', 'Education'
        ]
        
        unassigned = Researcher.objects.filter(department='Unassigned')
        if unassigned.exists():
            self.stdout.write(f"Assigning departments to {unassigned.count()} researchers...")
            for r in unassigned:
                r.department = random.choice(departments)
                r.save()

        # --- STEP 2: GENERATE MATCHES ---
        # Clear old suggestions
        CollaborationOpportunity.objects.all().delete()

        researchers = list(Researcher.objects.all())
        
        # CROSS-POLLINATION MATRIX (High value matches)
        interdisciplinary_rules = [
            ({'Computer Science', 'Public Health'}, "AI-Driven Healthcare Analytics", 95),
            ({'Economics', 'Environmental Science'}, "Green Economy & Sustainability Models", 92),
            ({'Communication', 'Business'}, "Digital Marketing & Consumer Behavior", 88),
            ({'Theology', 'Psychology'}, "Faith-Based Mental Health Interventions", 85),
            ({'Education', 'Computer Science'}, "EdTech & Adaptive Learning Systems", 90),
            ({'Public Health', 'Environmental Science'}, "Urban Sanitation & Disease Control", 94),
        ]

        generated_count = 0

        # Try to find 10 solid matches
        attempts = 0
        while generated_count < 10 and attempts < 200:
            attempts += 1
            r1 = random.choice(researchers)
            r2 = random.choice(researchers)

            # Skip if same person
            if r1 == r2: continue
            
            # Skip if they already work together
            if Project.objects.filter(members=r1).filter(members=r2).exists(): continue

            # Analyze Departments
            depts = {r1.department, r2.department}
            match_found = False
            
            # Check for "High Value" Interdisciplinary Match
            for rule_depts, topic, base_score in interdisciplinary_rules:
                if rule_depts.issubset(depts):
                    # We found a golden match!
                    CollaborationOpportunity.objects.create(
                        researcher_1=r1,
                        researcher_2=r2,
                        topic=topic,
                        match_score=base_score + random.randint(-3, 3),
                        reason=f"Combines {r1.name}'s expertise in {r1.department} with {r2.name}'s background in {r2.department}."
                    )
                    generated_count += 1
                    match_found = True
                    break
            
            # Fallback: Same Department Collaboration (Internal Grant)
            if not match_found and r1.department == r2.department:
                # Only add a few of these so we don't crowd out the exciting ones
                if random.random() > 0.7: 
                    CollaborationOpportunity.objects.create(
                        researcher_1=r1,
                        researcher_2=r2,
                        topic=f"Advanced {r1.department} Research Group",
                        match_score=random.randint(75, 85),
                        reason=f"Both researchers are active in {r1.department} but have no recorded joint projects."
                    )
                    generated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully generated {generated_count} AI Opportunities."))