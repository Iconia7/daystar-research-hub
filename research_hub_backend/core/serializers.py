from rest_framework import serializers
from .models import Researcher, Project, CollaborationOpportunity, SDG

class ResearcherSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    sdgs = serializers.SerializerMethodField()

    class Meta:
        model = Researcher
        fields = ['id', 'name', 'department', 'publications_count', 'h_index', 'citations', 'tags', 'sdgs']

    def get_tags(self, obj):
        return obj.get_tags_list()

    def get_sdgs(self, obj):
        # aggregating SDGs from their projects
        sdgs = set()
        for project in obj.projects.all():
            for sdg in project.sdgs.all():
                sdgs.add(sdg.number)
        return list(sdgs)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class OpportunitySerializer(serializers.ModelSerializer):
    r1_name = serializers.CharField(source='researcher_1.name')
    r2_name = serializers.CharField(source='researcher_2.name')
    r1_initials = serializers.CharField(source='researcher_1.initials')
    r2_initials = serializers.CharField(source='researcher_2.initials')

    class Meta:
        model = CollaborationOpportunity
        fields = ['id', 'r1_name', 'r2_name', 'r1_initials', 'r2_initials', 'topic', 'match_score', 'reason']

# --- THE GRAPH GENERATOR ---
# This converts Relational Data -> Graph JSON
def generate_graph_data():
    nodes = []
    links = []

    # 1. Add Researcher Nodes
    researchers = Researcher.objects.all()
    for r in researchers:
        nodes.append({
            "id": f"r_{r.id}",
            "name": r.name,
            "group": "person",
            "department": r.department,
            "val": r.publications_count or 10, # Node size based on pubs
            "stats": {
                "publications": r.publications_count,
                "hIndex": r.h_index,
                "citations": r.citations
            },
            "tags": r.get_tags_list(),
            "sdgs": [sdg.number for proj in r.projects.all() for sdg in proj.sdgs.all()]
        })

    # 2. Add Project Nodes
    projects = Project.objects.all()
    for p in projects:
        nodes.append({
            "id": f"p_{p.id}",
            "name": p.title,
            "group": "project",
            "department": "Project", # Visual category
            "val": 25, # Fixed size for projects
            "status": p.status
        })

        # 3. Create Links (Researcher <-> Project)
        for member in p.members.all():
            links.append({
                "source": f"r_{member.id}",
                "target": f"p_{p.id}",
                "value": 5 # Link strength
            })

    return {"nodes": nodes, "links": links}