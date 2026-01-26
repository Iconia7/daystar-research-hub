from django.db import models

class SDG(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"SDG {self.number}: {self.name}"

class Researcher(models.Model):
    name = models.CharField(max_length=200)
    initials = models.CharField(max_length=5, blank=True)
    department = models.CharField(max_length=100) # e.g., "Computer Science"
    email = models.EmailField(unique=True)
    
    # Stats for the "Right Panel" in your UI
    publications_count = models.IntegerField(default=0)
    h_index = models.IntegerField(default=0)
    citations = models.IntegerField(default=0)
    
    # Expertise Areas (Tags) - Stored as comma-separated text for simplicity with SQLite
    tags = models.TextField(help_text="Comma-separated tags e.g. 'AI, Flutter'") 
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')]

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=300)
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Completed', 'Completed')])
    start_year = models.IntegerField()
    
    # The team members (This creates the "Links" in the graph)
    members = models.ManyToManyField(Researcher, related_name='projects')
    sdgs = models.ManyToManyField(SDG, related_name='projects')

    def __str__(self):
        return self.title

class CollaborationOpportunity(models.Model):
    """
    Stores pre-calculated "AI Opportunities" [cite: 48]
    """
    researcher_1 = models.ForeignKey(Researcher, on_delete=models.CASCADE, related_name='opportunities_as_r1')
    researcher_2 = models.ForeignKey(Researcher, on_delete=models.CASCADE, related_name='opportunities_as_r2')
    topic = models.CharField(max_length=200) # e.g., "Theology x Economics"
    match_score = models.IntegerField() # e.g., 98
    reason = models.TextField() # Why they should collaborate

    def __str__(self):
        return f"{self.researcher_1} + {self.researcher_2}"