"""
Serializers for REST API endpoints.

Includes:
- ResearcherSerializer: Researcher profile with embeddings
- PublicationSerializer: Publication with SDG tags
- CollaborationSerializer: Researcher partnerships
- AuthorshipSerializer: Publication authorship
- Graph serializers: Nodes and links for visualization
"""
from rest_framework import serializers
from research_graph.models import (
    Researcher, Publication, Project, Thesis,
    Collaboration, Authorship, SDGChoices
)


class ResearcherSerializer(serializers.ModelSerializer):
    """Serializer for Researcher profiles."""
    
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Researcher
        fields = [
            'id', 'full_name', 'email', 'department',
            'research_interests', 'google_scholar_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
    
    def get_email(self, obj):
        return obj.user.email if obj.user else None
    
    def validate_department(self, value):
        """Validate department field."""
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("Department cannot be empty.")
        return value
    
    def validate_research_interests(self, value):
        """Validate research interests list."""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Research interests must be a list.")
        return value


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer for Publications."""
    
    sdg_labels = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_date',
            'doi', 'sdg_tags', 'sdg_labels', 'sdg_auto_generated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sdg_labels(self, obj):
        """Convert SDG choice codes to labels."""
        labels = []
        for sdg_code in obj.sdg_tags:
            for choice_val, choice_label in SDGChoices.choices:
                if choice_val == sdg_code:
                    labels.append(str(choice_label))
                    break
        return labels
    
    def validate_title(self, value):
        """Validate publication title."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty.")
        return value
    
    def validate_doi(self, value):
        """Validate DOI format."""
        if value and not value.startswith('10.'):
            raise serializers.ValidationError("Invalid DOI format. Must start with '10.'")
        return value


class CollaborationSerializer(serializers.ModelSerializer):
    """Serializer for Collaborations between researchers."""
    
    researcher_1_name = serializers.CharField(
        source='researcher_1.user.get_full_name',
        read_only=True
    )
    researcher_2_name = serializers.CharField(
        source='researcher_2.user.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Collaboration
        fields = [
            'id', 'researcher_1', 'researcher_2',
            'researcher_1_name', 'researcher_2_name',
            'strength', 'last_collaborated',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_strength(self, value):
        """Validate collaboration strength."""
        if value and value < 0:
            raise serializers.ValidationError("Strength must be non-negative.")
        return value


class AuthorshipSerializer(serializers.ModelSerializer):
    """Serializer for Authorship relationships."""
    
    researcher_name = serializers.CharField(
        source='researcher.user.get_full_name',
        read_only=True
    )
    publication_title = serializers.CharField(
        source='publication.title',
        read_only=True
    )
    
    class Meta:
        model = Authorship
        fields = [
            'id', 'researcher', 'researcher_name',
            'publication', 'publication_title',
            'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_order(self, value):
        """Validate author order."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Author order must be non-negative.")
        return value


# ==================== Graph Visualization Serializers ====================


class GraphNodeSerializer(serializers.Serializer):
    """Serializer for graph nodes (researchers and publications)."""
    
    id = serializers.IntegerField()
    label = serializers.CharField(max_length=500)
    type = serializers.CharField(max_length=20)  # 'researcher' or 'publication'
    cluster_id = serializers.CharField(max_length=255, required=False, allow_null=True)
    data = serializers.JSONField()  # Additional metadata


class GraphLinkSerializer(serializers.Serializer):
    """Serializer for graph links (edges between nodes)."""
    
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    type = serializers.CharField(max_length=20)  # 'collaboration' or 'authorship'
    value = serializers.FloatField()  # strength or weight
    metadata = serializers.JSONField(required=False)


class ResearchGraphDataSerializer(serializers.Serializer):
    """
    Serializer for complete graph data (nodes + links).
    
    Used for frontend visualization with D3.js, React Flow, or similar.
    """
    
    nodes = GraphNodeSerializer(many=True)
    links = GraphLinkSerializer(many=True)
    summary = serializers.JSONField()


# ==================== Helper Functions ====================


def create_researcher_node(researcher):
    """Convert Researcher to graph node."""
    return {
        'id': f"researcher_{researcher.id}",
        'label': researcher.user.get_full_name(),
        'type': 'researcher',
        'cluster_id': researcher.department,
        'data': {
            'researcher_id': researcher.id,
            'department': researcher.department,
            'interests': researcher.research_interests,
            'email': researcher.user.email,
        }
    }


def create_publication_node(publication):
    """Convert Publication to graph node."""
    return {
        'id': f"publication_{publication.id}",
        'label': publication.title[:100],  # Truncate long titles
        'type': 'publication',
        'cluster_id': None,
        'data': {
            'publication_id': publication.id,
            'title': publication.title,
            'date': publication.publication_date.isoformat() if publication.publication_date else None,
            'doi': publication.doi,
            'sdg_tags': publication.sdg_tags,
        }
    }


def create_collaboration_link(collaboration):
    """Convert Collaboration to graph link."""
    return {
        'source': f"researcher_{collaboration.researcher_1_id}",
        'target': f"researcher_{collaboration.researcher_2_id}",
        'type': 'collaboration',
        'value': collaboration.strength,
        'metadata': {
            'last_collaborated': collaboration.last_collaborated.isoformat() if collaboration.last_collaborated else None,
        }
    }


def create_authorship_link(authorship):
    """Convert Authorship to graph link."""
    return {
        'source': f"researcher_{authorship.researcher_id}",
        'target': f"publication_{authorship.publication_id}",
        'type': 'authorship',
        'value': 1.0,  # Static value for authorship
        'metadata': {
            'author_order': authorship.order,
        }
    }
