"""
URL Configuration for research_graph app

Includes endpoints for:
- Authentication (JWT tokens, registration, login, profile)
- CRUD operations (researchers, publications, collaborations, authorships)
- Analytics and dashboards
- Graph visualization (nodes and links)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views, auth, viewsets

# Create router for ViewSets
router = DefaultRouter()
router.register(r'researchers', viewsets.ResearcherViewSet, basename='researcher')
router.register(r'publications', viewsets.PublicationViewSet, basename='publication')
router.register(r'collaborations', viewsets.CollaborationViewSet, basename='collaboration')
router.register(r'authorships', viewsets.AuthorshipViewSet, basename='authorship')

app_name = 'research_graph'

urlpatterns = [
    # ==================== Authentication Endpoints ====================
    
    # JWT Token endpoints
    path('api/auth/login/', auth.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('api/auth/register/', auth.register_view, name='register'),
    path('api/auth/me/', auth.current_user_view, name='current_user'),
    path('api/auth/logout/', auth.logout_view, name='logout'),
    path('api/auth/profile/', auth.update_profile_view, name='update_profile'),
    
    # ==================== API Documentation ====================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ==================== CRUD Endpoints (ViewSets) ====================
    path('api/', include(router.urls)),
    
    # ==================== Analytics Endpoints ====================
    path('api/analytics/', views.ResearchAnalyticsView.as_view(), name='analytics'),
    path('api/analytics/sdg-distribution/', views.SDGDistributionView.as_view(), name='sdg-distribution'),
    path('api/analytics/department-performance/', views.DepartmentPerformanceView.as_view(), name='department-performance'),
    path('api/analytics/collaboration-metrics/', views.CollaborationMetricsView.as_view(), name='collaboration-metrics'),
    
    # ==================== Graph Visualization Endpoints ====================
    path('api/graph/', views.ResearchGraphDataView.as_view(), name='graph-data'),
    path('api/graph/researchers/', views.ResearcherGraphView.as_view(), name='graph-researchers'),
    path('api/graph/publications/', views.PublicationGraphView.as_view(), name='graph-publications'),
]

