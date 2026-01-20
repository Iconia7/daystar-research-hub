from django.apps import AppConfig


class ResearchGraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'research_graph'
    
    def ready(self):
        """Register signal handlers when the app is ready."""
        import research_graph.signals  # noqa: F401
