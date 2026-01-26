from django.urls import path
from .views import GraphDataView, ResearcherListView, ProjectListView, OpportunityListView

urlpatterns = [
    path('graph/', GraphDataView.as_view(), name='graph-data'),
    path('researchers/', ResearcherListView.as_view(), name='researchers-list'),
    path('projects/', ProjectListView.as_view(), name='projects-list'),
    path('opportunities/', OpportunityListView.as_view(), name='opportunities-list'),
]