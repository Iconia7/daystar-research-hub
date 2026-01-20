"""
Analytics Service for Research Collaboration Graph

Provides aggregated statistics and insights for:
- SDG distribution across publications
- Department performance metrics
- Collaboration network analysis
- Research trends

Uses Django ORM aggregation for efficient database queries.
"""
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import Coalesce
from research_graph.models import (
    Publication, Researcher, Project, Collaboration, 
    Authorship, SDGChoices
)


class ResearchAnalyticsService:
    """
    Analytics service providing research metrics and insights.
    
    All methods return dictionaries suitable for JSON serialization
    and use Django ORM aggregation for efficiency.
    """
    
    @staticmethod
    def get_sdg_distribution() -> dict:
        """
        Calculate distribution of publications across SDGs.
        
        Returns:
            {
                'sdg_data': [
                    {'sdg': 'SDG_1', 'label': 'No Poverty', 'count': 10},
                    {'sdg': 'SDG_3', 'label': 'Good Health', 'count': 15},
                    ...
                ],
                'total_papers': 100,
                'covered_by_sdg': 85
            }
        """
        sdg_counts = {}
        
        # Count publications for each SDG
        publications = Publication.objects.all()
        
        for sdg_value, sdg_label in SDGChoices.choices:
            # Count publications containing this SDG in array
            count = publications.filter(sdg_tags__contains=[sdg_value]).count()
            if count > 0:
                sdg_counts[sdg_value] = {
                    'sdg': sdg_value,
                    'label': str(sdg_label),
                    'count': count,
                    'percentage': 0  # Will calculate below
                }
        
        total_papers = publications.count()
        papers_with_sdg = sum(count['count'] for count in sdg_counts.values())
        
        # Calculate percentages
        if papers_with_sdg > 0:
            for sdg_data in sdg_counts.values():
                sdg_data['percentage'] = round(
                    (sdg_data['count'] / papers_with_sdg) * 100, 2
                )
        
        return {
            'sdg_data': sorted(
                sdg_counts.values(),
                key=lambda x: x['count'],
                reverse=True
            ),
            'total_papers': total_papers,
            'covered_by_sdg': papers_with_sdg,
            'sdg_coverage_rate': round(
                (papers_with_sdg / total_papers * 100) if total_papers > 0 else 0, 2
            )
        }
    
    @staticmethod
    def get_department_performance() -> dict:
        """
        Calculate publication and collaboration metrics by department.
        
        Returns:
            {
                'departments': [
                    {
                        'name': 'Computer Science',
                        'researcher_count': 15,
                        'publication_count': 45,
                        'collaboration_strength': 2.3,
                        'avg_collaborators': 4.5
                    },
                    ...
                ],
                'total_researchers': 50,
                'total_publications': 200
            }
        """
        departments = {}
        
        # Get all departments
        for dept in Researcher.objects.values_list('department', flat=True).distinct():
            if not dept:  # Skip null departments
                continue
            
            researchers = Researcher.objects.filter(department=dept)
            researcher_ids = list(researchers.values_list('id', flat=True))
            
            # Count publications by researchers in department
            publications = Authorship.objects.filter(
                researcher_id__in=researcher_ids
            ).count()
            
            # Calculate collaboration metrics
            collaborations = Collaboration.objects.filter(
                Q(researcher_1_id__in=researcher_ids) |
                Q(researcher_2_id__in=researcher_ids)
            )
            
            collaboration_strength = collaborations.aggregate(
                avg_strength=Avg('strength')
            )['avg_strength'] or 0
            
            # Average collaborators per researcher
            if researcher_ids:
                total_connections = collaborations.count()
                avg_collaborators = total_connections / len(researcher_ids)
            else:
                avg_collaborators = 0
            
            departments[dept] = {
                'name': dept,
                'researcher_count': len(researcher_ids),
                'publication_count': publications,
                'collaboration_strength': round(collaboration_strength, 2),
                'avg_collaborators': round(avg_collaborators, 2),
                'publications_per_researcher': round(
                    publications / len(researcher_ids) if researcher_ids else 0, 2
                )
            }
        
        total_researchers = Researcher.objects.count()
        total_publications = Authorship.objects.count()
        
        return {
            'departments': sorted(
                departments.values(),
                key=lambda x: x['publication_count'],
                reverse=True
            ),
            'total_researchers': total_researchers,
            'total_publications': total_publications
        }
    
    @staticmethod
    def get_collaboration_metrics() -> dict:
        """
        Calculate network collaboration metrics.
        
        Returns:
            {
                'total_collaborations': 150,
                'avg_strength': 2.5,
                'collaboration_range': {'min': 1, 'max': 15},
                'strength_distribution': {
                    '1-2': 45,
                    '3-5': 60,
                    '6-10': 30,
                    '10+': 15
                },
                'most_connected_researchers': [
                    {'researcher': 'Dr. Alice', 'collaborators': 12, 'avg_strength': 3.2},
                    ...
                ]
            }
        """
        collaborations = Collaboration.objects.all()
        total = collaborations.count()
        
        if total == 0:
            return {
                'total_collaborations': 0,
                'avg_strength': 0,
                'collaboration_range': {'min': 0, 'max': 0},
                'strength_distribution': {},
                'most_connected_researchers': []
            }
        
        # Get basic metrics
        stats = collaborations.aggregate(
            avg_strength=Avg('strength'),
            min_strength=Count('strength', distinct=True),
            max_strength=Count('strength', distinct=True)
        )
        
        # Get actual min/max
        min_strength = collaborations.order_by('strength').first().strength
        max_strength = collaborations.order_by('-strength').first().strength
        
        # Strength distribution
        strength_dist = {
            '1-2': collaborations.filter(strength__range=(1, 2)).count(),
            '3-5': collaborations.filter(strength__range=(3, 5)).count(),
            '6-10': collaborations.filter(strength__range=(6, 10)).count(),
            '10+': collaborations.filter(strength__gt=10).count(),
        }
        
        # Most connected researchers
        most_connected = []
        for researcher in Researcher.objects.all():
            connections = Collaboration.objects.filter(
                Q(researcher_1=researcher) | Q(researcher_2=researcher)
            )
            
            if connections.exists():
                avg_strength = connections.aggregate(
                    avg=Avg('strength')
                )['avg'] or 0
                
                most_connected.append({
                    'researcher': researcher.user.get_full_name(),
                    'department': researcher.department,
                    'collaborators': connections.count(),
                    'avg_strength': round(avg_strength, 2),
                    'total_strength': sum(c.strength for c in connections)
                })
        
        # Sort by collaborators and take top 10
        most_connected = sorted(
            most_connected,
            key=lambda x: x['collaborators'],
            reverse=True
        )[:10]
        
        return {
            'total_collaborations': total,
            'avg_strength': round(stats['avg_strength'] or 0, 2),
            'collaboration_range': {
                'min': min_strength,
                'max': max_strength
            },
            'strength_distribution': strength_dist,
            'most_connected_researchers': most_connected
        }
    
    @staticmethod
    def get_project_metrics() -> dict:
        """
        Calculate project statistics.
        
        Returns:
            {
                'total_projects': 20,
                'by_status': {
                    'active': 12,
                    'completed': 5,
                    'paused': 2,
                    'planned': 1
                },
                'by_funding_body': {
                    'NSF': 8,
                    'NIH': 5,
                    'Other': 7
                },
                'avg_project_duration_months': 24
            }
        """
        projects = Project.objects.all()
        total = projects.count()
        
        # By status
        by_status = {}
        for status_value, status_label in Project.ProjectStatus.choices:
            count = projects.filter(status=status_value).count()
            by_status[status_value] = count
        
        # By funding body
        by_funding = projects.values_list(
            'funding_body'
        ).annotate(count=Count('id'))
        
        funding_dict = {
            (name or 'Unknown'): count 
            for name, count in by_funding
        }
        
        # Average duration
        from django.db.models import F
        from datetime import timedelta
        projects_with_dates = projects.filter(
            start_date__isnull=False,
            end_date__isnull=False
        )
        
        if projects_with_dates.exists():
            total_days = sum(
                (p.end_date - p.start_date).days 
                for p in projects_with_dates
            )
            avg_months = round(total_days / projects_with_dates.count() / 30, 1)
        else:
            avg_months = 0
        
        return {
            'total_projects': total,
            'by_status': by_status,
            'by_funding_body': dict(sorted(
                funding_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )),
            'avg_project_duration_months': avg_months
        }
    
    @staticmethod
    def get_complete_analytics() -> dict:
        """
        Get all analytics metrics in one call.
        
        Returns:
            Complete analytics object with all metrics
        """
        return {
            'sdg_distribution': ResearchAnalyticsService.get_sdg_distribution(),
            'department_performance': ResearchAnalyticsService.get_department_performance(),
            'collaboration_metrics': ResearchAnalyticsService.get_collaboration_metrics(),
            'project_metrics': ResearchAnalyticsService.get_project_metrics(),
            'summary': {
                'total_researchers': Researcher.objects.count(),
                'total_publications': Publication.objects.count(),
                'total_projects': Project.objects.count(),
                'total_collaborations': Collaboration.objects.count(),
                'departments': Researcher.objects.values_list(
                    'department', flat=True
                ).distinct().count()
            }
        }
