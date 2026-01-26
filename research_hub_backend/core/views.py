from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .models import Researcher, Project, CollaborationOpportunity
from .serializers import ResearcherSerializer, ProjectSerializer, OpportunitySerializer, generate_graph_data

class GraphDataView(APIView):
    """
    Returns the { nodes: [], links: [] } structure for the Graph Canvas.
    """
    def get(self, request):
        data = generate_graph_data()
        return Response(data)

class ResearcherListView(generics.ListAPIView):
    """
    For the 'Researchers' tab
    """
    queryset = Researcher.objects.all()
    serializer_class = ResearcherSerializer

class ProjectListView(generics.ListAPIView):
    """
    For the 'Projects' tab
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class OpportunityListView(generics.ListAPIView):
    """
    For the 'Opportunities' tab (AI Suggestions)
    """
    queryset = CollaborationOpportunity.objects.order_by('-match_score')
    serializer_class = OpportunitySerializer