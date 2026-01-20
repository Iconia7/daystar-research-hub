from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Prefetch
from .analytics import ResearchAnalyticsService
from .models import Researcher, Publication, Collaboration, Authorship
from .serializers import (
    ResearcherSerializer, PublicationSerializer,
    create_researcher_node, create_publication_node,
    create_collaboration_link, create_authorship_link
)


# ==================== Error Handling Utilities ====================


class APIException(Exception):
    """Base API exception with HTTP status."""
    def __init__(self, message, status_code=HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APIException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, HTTP_404_NOT_FOUND)


class ValidationError(APIException):
    def __init__(self, message="Invalid request parameters"):
        super().__init__(message, HTTP_400_BAD_REQUEST)


def handle_api_exception(func):
    """Decorator to handle APIException in views."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIException as e:
            return Response(
                {"error": e.message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "detail": str(e)},
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper


class ResearchAnalyticsView(APIView):
    """
    API endpoint providing comprehensive research analytics.
    
    Returns aggregated statistics about:
    - SDG (Sustainable Development Goals) distribution
    - Department performance
    - Collaboration network metrics
    - Project statistics
    
    All data is computed using efficient Django ORM aggregations.
    No N+1 queries or Python loops for data processing.
    
    Endpoint: GET /api/analytics/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Return complete analytics dashboard data.
        
        Response format:
        {
            "sdg_distribution": {...},
            "department_performance": {...},
            "collaboration_metrics": {...},
            "project_metrics": {...},
            "summary": {...}
        }
        """
        try:
            analytics_data = ResearchAnalyticsService.get_complete_analytics()
            return Response(analytics_data, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error": "Failed to generate analytics",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class SDGDistributionView(APIView):
    """
    API endpoint for SDG distribution statistics.
    
    Endpoint: GET /api/analytics/sdg-distribution/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Return SDG distribution breakdown."""
        try:
            data = ResearchAnalyticsService.get_sdg_distribution()
            return Response(data, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error": "Failed to get SDG distribution",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepartmentPerformanceView(APIView):
    """
    API endpoint for department performance metrics.
    
    Endpoint: GET /api/analytics/department-performance/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Return department performance metrics."""
        try:
            data = ResearchAnalyticsService.get_department_performance()
            return Response(data, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error": "Failed to get department performance",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class CollaborationMetricsView(APIView):
    """
    API endpoint for collaboration network metrics.
    
    Endpoint: GET /api/analytics/collaboration-metrics/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Return collaboration network metrics."""
        try:
            data = ResearchAnalyticsService.get_collaboration_metrics()
            return Response(data, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error": "Failed to get collaboration metrics",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== Graph Visualization Views ====================


class ResearchGraphDataView(APIView):
    """
    API endpoint for complete graph data (nodes + links).
    
    Returns researchers and publications as nodes, and collaborations and
    authorships as links. Optimized for frontend visualization with D3.js,
    React Flow, or similar libraries.
    
    Endpoint: GET /api/graph/
    
    Response format:
    {
        "nodes": [
            {
                "id": "researcher_1",
                "label": "Dr. Alice Smith",
                "type": "researcher",
                "cluster_id": "Computer Science",
                "data": {...}
            },
            {
                "id": "publication_42",
                "label": "Deep Learning for Climate Prediction",
                "type": "publication",
                "cluster_id": null,
                "data": {...}
            }
        ],
        "links": [
            {
                "source": "researcher_1",
                "target": "researcher_5",
                "type": "collaboration",
                "value": 3
            },
            {
                "source": "researcher_1",
                "target": "publication_42",
                "type": "authorship",
                "value": 1
            }
        ],
        "summary": {
            "total_nodes": 150,
            "total_links": 450,
            "researcher_count": 100,
            "publication_count": 50,
            "collaboration_count": 250,
            "authorship_count": 200
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Return graph data for visualization.
        
        Query Parameters:
        - department: Filter by department (e.g., ?department=Computer%20Science)
        - min_collaboration_strength: Filter collaborations by min strength (default: 1)
        - exclude_isolated: Exclude nodes with no connections (default: false)
        """
        try:
            # Get query parameters
            department = request.query_params.get('department', None)
            try:
                min_strength = int(request.query_params.get('min_collaboration_strength', 1))
            except (ValueError, TypeError):
                raise ValidationError("min_collaboration_strength must be an integer")
            
            exclude_isolated = request.query_params.get('exclude_isolated', 'false').lower() == 'true'
            
            nodes = []
            links = []
            
            # ==================== Build Nodes ====================
            
            # Get researchers (with optimizations)
            researchers_query = Researcher.objects.select_related('user')
            if department:
                researchers_query = researchers_query.filter(department=department)
            researchers = list(researchers_query)
            
            # Get publications (with optimizations)
            publications = list(Publication.objects.all())
            
            # Create nodes
            for researcher in researchers:
                nodes.append(create_researcher_node(researcher))
            
            for publication in publications:
                nodes.append(create_publication_node(publication))
            
            # ==================== Build Links ====================
            
            # Get collaborations (edges between researchers)
            collaborations = Collaboration.objects.select_related(
                'researcher_1', 'researcher_2'
            ).filter(strength__gte=min_strength)
            
            for collab in collaborations:
                links.append(create_collaboration_link(collab))
            
            # Get authorships (edges between researchers and publications)
            authorships = Authorship.objects.select_related(
                'researcher', 'publication'
            )
            
            for authorship in authorships:
                links.append(create_authorship_link(authorship))
            
            # ==================== Optional Filtering ====================
            
            if exclude_isolated:
                # Find nodes that appear in at least one link
                connected_node_ids = set()
                for link in links:
                    connected_node_ids.add(link['source'])
                    connected_node_ids.add(link['target'])
                
                # Filter nodes
                nodes = [n for n in nodes if n['id'] in connected_node_ids]
            
            # ==================== Build Response ====================
            
            response_data = {
                'nodes': nodes,
                'links': links,
                'summary': {
                    'total_nodes': len(nodes),
                    'total_links': len(links),
                    'researcher_count': sum(1 for n in nodes if n['type'] == 'researcher'),
                    'publication_count': sum(1 for n in nodes if n['type'] == 'publication'),
                    'collaboration_count': sum(1 for l in links if l['type'] == 'collaboration'),
                    'authorship_count': sum(1 for l in links if l['type'] == 'authorship'),
                    'filters_applied': {
                        'department': department,
                        'min_collaboration_strength': min_strength,
                        'exclude_isolated': exclude_isolated,
                    }
                }
            }
            
            return Response(response_data, status=HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {
                    "error": "Failed to generate graph data",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResearcherGraphView(APIView):
    """
    API endpoint for researcher-focused graph.
    
    Returns only researcher nodes and collaboration links.
    Useful for visualizing the collaboration network.
    
    Endpoint: GET /api/graph/researchers/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Return researcher collaboration network."""
        try:
            # Get parameters
            department = request.query_params.get('department', None)
            try:
                min_strength = int(request.query_params.get('min_collaboration_strength', 1))
            except (ValueError, TypeError):
                raise ValidationError("min_collaboration_strength must be an integer")
            
            # Get researchers
            researchers_query = Researcher.objects.select_related('user')
            if department:
                researchers_query = researchers_query.filter(department=department)
            researchers = list(researchers_query)
            
            # Create nodes
            nodes = [create_researcher_node(r) for r in researchers]
            researcher_ids = {r.id for r in researchers}
            
            # Get collaborations
            collaborations = Collaboration.objects.select_related(
                'researcher_1', 'researcher_2'
            ).filter(
                strength__gte=min_strength,
                researcher_1_id__in=researcher_ids,
                researcher_2_id__in=researcher_ids
            )
            
            # Create links
            links = [create_collaboration_link(c) for c in collaborations]
            
            response_data = {
                'nodes': nodes,
                'links': links,
                'summary': {
                    'total_researchers': len(nodes),
                    'total_collaborations': len(links),
                    'department': department,
                }
            }
            
            return Response(response_data, status=HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {
                    "error": "Failed to generate researcher graph",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicationGraphView(APIView):
    """
    API endpoint for publication-focused graph.
    
    Returns publication nodes and authorship edges.
    Useful for visualizing research output and author networks.
    
    Endpoint: GET /api/graph/publications/
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Return publication and authorship network."""
        try:
            # Get parameters
            department = request.query_params.get('department', None)
            year_from = request.query_params.get('year_from', None)
            year_to = request.query_params.get('year_to', None)
            
            # Validate year parameters
            if year_from:
                try:
                    year_from = int(year_from)
                except (ValueError, TypeError):
                    raise ValidationError("year_from must be an integer")
            
            if year_to:
                try:
                    year_to = int(year_to)
                except (ValueError, TypeError):
                    raise ValidationError("year_to must be an integer")
            
            # Get publications
            pubs_query = Publication.objects.all()
            
            if year_from:
                pubs_query = pubs_query.filter(publication_date__year__gte=year_from)
            if year_to:
                pubs_query = pubs_query.filter(publication_date__year__lte=year_to)
            
            publications = list(pubs_query)
            
            # Get researchers for these publications
            researchers_query = Researcher.objects.select_related('user')
            if department:
                researchers_query = researchers_query.filter(department=department)
            researchers = list(researchers_query)
            researcher_ids = {r.id for r in researchers}
            
            # Create publication nodes
            nodes = [create_publication_node(p) for p in publications]
            
            # Get authorships
            authorships = Authorship.objects.select_related(
                'researcher', 'publication'
            ).filter(
                researcher_id__in=researcher_ids,
                publication_id__in=[p.id for p in publications]
            )
            
            # Create links
            links = [create_authorship_link(a) for a in authorships]
            
            response_data = {
                'nodes': nodes,
                'links': links,
                'summary': {
                    'total_publications': len(nodes),
                    'total_authors': len(set(a.researcher_id for a in authorships)),
                    'filters_applied': {
                        'department': department,
                        'year_from': year_from,
                        'year_to': year_to,
                    }
                }
            }
            
            return Response(response_data, status=HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {
                    "error": "Failed to generate publication graph",
                    "detail": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )
