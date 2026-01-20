"""
Comprehensive CRUD ViewSets for all models with proper error handling and pagination.

Includes:
- ResearcherViewSet: Full CRUD for researchers
- PublicationViewSet: Full CRUD for publications
- CollaborationViewSet: Full CRUD for collaborations
- AuthorshipViewSet: Full CRUD for authorships
- Custom error handling and validation
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Researcher, Publication, Collaboration, Authorship
from .serializers import (
    ResearcherSerializer, PublicationSerializer,
    CollaborationSerializer, AuthorshipSerializer
)


class ResearcherViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for researchers.
    
    Endpoints:
    - GET /api/researchers/ - List all researchers (paginated)
    - POST /api/researchers/ - Create researcher
    - GET /api/researchers/{id}/ - Get researcher details
    - PUT /api/researchers/{id}/ - Update researcher
    - DELETE /api/researchers/{id}/ - Delete researcher
    - GET /api/researchers/?search=name - Search by name/email
    - GET /api/researchers/?department=CS - Filter by department
    - GET /api/researchers/?ordering=-created_at - Order results
    """
    
    queryset = Researcher.objects.select_related('user').all()
    serializer_class = ResearcherSerializer
    permission_classes = [AllowAny]  # Allow read, but require auth for write
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'research_interests']
    ordering_fields = ['user__last_name', 'user__first_name', 'created_at', 'updated_at']
    ordering = ['user__last_name', 'user__first_name']
    
    def get_permissions(self):
        """Allow anyone to read, but require authentication for write."""
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create researcher with proper error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update researcher with proper error handling."""
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def collaborators(self, request, pk=None):
        """Get all collaborators of a researcher."""
        try:
            researcher = self.get_object()
            collaborations = Collaboration.objects.filter(
                models.Q(researcher_1=researcher) | models.Q(researcher_2=researcher)
            ).select_related('researcher_1', 'researcher_2', 'researcher_1__user', 'researcher_2__user')
            
            collaborators = []
            for collab in collaborations:
                other = collab.researcher_2 if collab.researcher_1_id == researcher.id else collab.researcher_1
                collaborators.append({
                    'researcher': ResearcherSerializer(other).data,
                    'strength': collab.strength,
                    'last_collaborated': collab.last_collaborated
                })
            
            return Response(collaborators, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicationViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for publications.
    
    Endpoints:
    - GET /api/publications/ - List all publications (paginated)
    - POST /api/publications/ - Create publication
    - GET /api/publications/{id}/ - Get publication details
    - PUT /api/publications/{id}/ - Update publication
    - DELETE /api/publications/{id}/ - Delete publication
    - GET /api/publications/?search=title - Search by title/abstract
    - GET /api/publications/?year_from=2020&year_to=2024 - Filter by year
    - GET /api/publications/?sdg_tags=SDG_13 - Filter by SDG tags
    """
    
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'abstract', 'doi']
    ordering_fields = ['publication_date', 'created_at', 'title']
    ordering = ['-publication_date']
    
    def get_permissions(self):
        """Allow anyone to read, but require authentication for write."""
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Apply additional filters."""
        queryset = Publication.objects.all()
        
        # Year range filtering
        year_from = self.request.query_params.get('year_from')
        year_to = self.request.query_params.get('year_to')
        
        if year_from:
            try:
                queryset = queryset.filter(publication_date__year__gte=int(year_from))
            except (ValueError, TypeError):
                pass
        
        if year_to:
            try:
                queryset = queryset.filter(publication_date__year__lte=int(year_to))
            except (ValueError, TypeError):
                pass
        
        # SDG tags filtering
        sdg_tags = self.request.query_params.get('sdg_tags')
        if sdg_tags:
            sdg_list = [tag.strip() for tag in sdg_tags.split(',')]
            queryset = queryset.filter(sdg_tags__overlap=sdg_list)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create publication with proper error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update publication with proper error handling."""
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)


class CollaborationViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for collaborations.
    
    Endpoints:
    - GET /api/collaborations/ - List all collaborations
    - POST /api/collaborations/ - Create collaboration
    - GET /api/collaborations/{id}/ - Get collaboration details
    - PUT /api/collaborations/{id}/ - Update collaboration
    - DELETE /api/collaborations/{id}/ - Delete collaboration
    - GET /api/collaborations/?researcher_1=1 - Filter by researcher
    - GET /api/collaborations/?min_strength=2 - Filter by strength
    """
    
    queryset = Collaboration.objects.select_related('researcher_1', 'researcher_2', 
                                                     'researcher_1__user', 'researcher_2__user').all()
    serializer_class = CollaborationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['researcher_1', 'researcher_2']
    ordering_fields = ['strength', 'last_collaborated', 'created_at']
    ordering = ['-strength']
    
    def get_permissions(self):
        """Allow anyone to read, but require authentication for write."""
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Apply strength filtering."""
        queryset = Collaboration.objects.select_related(
            'researcher_1', 'researcher_2', 'researcher_1__user', 'researcher_2__user'
        ).all()
        
        min_strength = self.request.query_params.get('min_strength')
        if min_strength:
            try:
                queryset = queryset.filter(strength__gte=int(min_strength))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create collaboration with proper error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)


class AuthorshipViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for authorships.
    
    Endpoints:
    - GET /api/authorships/ - List all authorships
    - POST /api/authorships/ - Create authorship
    - GET /api/authorships/{id}/ - Get authorship details
    - PUT /api/authorships/{id}/ - Update authorship
    - DELETE /api/authorships/{id}/ - Delete authorship
    - GET /api/authorships/?researcher=1 - Filter by researcher
    - GET /api/authorships/?publication=5 - Filter by publication
    """
    
    queryset = Authorship.objects.select_related(
        'researcher', 'publication', 'researcher__user'
    ).all()
    serializer_class = AuthorshipSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['researcher', 'publication']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_permissions(self):
        """Allow anyone to read, but require authentication for write."""
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create authorship with proper error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
