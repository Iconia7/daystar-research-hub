from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from pgvector.django import VectorField


class SDGChoices(models.TextChoices):
    """UN Sustainable Development Goals (SDG) 1-17"""
    SDG_1 = "SDG_1", _("No Poverty")
    SDG_2 = "SDG_2", _("Zero Hunger")
    SDG_3 = "SDG_3", _("Good Health and Well-being")
    SDG_4 = "SDG_4", _("Quality Education")
    SDG_5 = "SDG_5", _("Gender Equality")
    SDG_6 = "SDG_6", _("Clean Water and Sanitation")
    SDG_7 = "SDG_7", _("Affordable and Clean Energy")
    SDG_8 = "SDG_8", _("Decent Work and Economic Growth")
    SDG_9 = "SDG_9", _("Industry, Innovation and Infrastructure")
    SDG_10 = "SDG_10", _("Reduced Inequalities")
    SDG_11 = "SDG_11", _("Sustainable Cities and Communities")
    SDG_12 = "SDG_12", _("Responsible Consumption and Production")
    SDG_13 = "SDG_13", _("Climate Action")
    SDG_14 = "SDG_14", _("Life Below Water")
    SDG_15 = "SDG_15", _("Life on Land")
    SDG_16 = "SDG_16", _("Peace, Justice and Strong Institutions")
    SDG_17 = "SDG_17", _("Partnerships for the Goals")


class Researcher(models.Model):
    """
    Core entity representing a researcher in the collaboration graph.
    Extends Django's User model with additional research-specific fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='researcher_profile')
    department = models.CharField(max_length=255, blank=True, null=True)
    research_interests = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="List of research interests/keywords"
    )
    google_scholar_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Google Scholar ID for the researcher"
    )
    interests_embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding of research interests for semantic search"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Researcher"
        verbose_name_plural = "Researchers"
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"


class Publication(models.Model):
    """
    Represents a research publication linked to researchers via Authorship.
    
    Features:
    - Auto-generates SDG tags based on abstract content
    - Auto-generates vector embedding from abstract
    - Tracks publication metadata (DOI, date, authors)
    """
    title = models.CharField(max_length=500)
    abstract = models.TextField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    doi = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="DOI"
    )
    sdg_tags = ArrayField(
        models.CharField(max_length=10, choices=SDGChoices.choices),
        default=list,
        help_text="UN Sustainable Development Goals associated with this publication"
    )
    sdg_auto_generated = models.BooleanField(
        default=False,
        help_text="Indicates if SDG tags were auto-generated from abstract"
    )
    abstract_embedding = VectorField(
        dimensions=1536,
        null=True,
        blank=True,
        help_text="Vector embedding of publication abstract for semantic search"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['publication_date']),
        ]

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate SDG tags from abstract.
        
        When a publication is saved:
        1. If SDG tags are empty and abstract exists, classify the abstract
        2. Auto-detected tags are marked with sdg_auto_generated flag
        3. User can manually override by providing sdg_tags
        """
        # Auto-detect SDGs if not already provided and abstract exists
        if not self.sdg_tags and self.abstract:
            from .utils import SDGClassifier
            detected_sdgs = SDGClassifier.classify_publication(
                title=self.title,
                abstract=self.abstract,
                threshold=0.3  # Adjust based on precision needs
            )
            if detected_sdgs:
                self.sdg_tags = detected_sdgs
                self.sdg_auto_generated = True
        else:
            # User provided manual tags or no abstract
            self.sdg_auto_generated = False
        
        # Call parent save
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Project(models.Model):
    """
    Represents a research project that may involve multiple researchers.
    """
    class ProjectStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETED = "completed", _("Completed")
        PAUSED = "paused", _("Paused")
        PLANNED = "planned", _("Planned")

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    funding_body = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.ACTIVE
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class Thesis(models.Model):
    """
    Represents a thesis (Master's or PhD) with a supervisor relationship.
    """
    class ThesisType(models.TextChoices):
        MASTERS = "masters", _("Master's Thesis")
        PHD = "phd", _("PhD Dissertation")
        BACHELOR = "bachelor", _("Bachelor Thesis")

    title = models.CharField(max_length=500)
    thesis_type = models.CharField(
        max_length=20,
        choices=ThesisType.choices,
        default=ThesisType.MASTERS
    )
    student = models.CharField(max_length=255)
    supervisor = models.ForeignKey(
        Researcher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_theses'
    )
    abstract = models.TextField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thesis"
        verbose_name_plural = "Theses"
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.title} - {self.student}"


# ==================== Edge Models (Relationships) ====================


class Collaboration(models.Model):
    """
    Intermediary model representing collaboration between two researchers.
    Stores metadata about the collaboration edge (strength, last_collaborated).
    """
    researcher_1 = models.ForeignKey(
        Researcher,
        on_delete=models.CASCADE,
        related_name='collaborations_initiated'
    )
    researcher_2 = models.ForeignKey(
        Researcher,
        on_delete=models.CASCADE,
        related_name='collaborations_received'
    )
    strength = models.IntegerField(
        default=1,
        help_text="Strength of collaboration (e.g., number of joint publications)"
    )
    last_collaborated = models.DateField(
        blank=True,
        null=True,
        help_text="Date of most recent collaboration"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Collaboration"
        verbose_name_plural = "Collaborations"
        unique_together = ('researcher_1', 'researcher_2')
        indexes = [
            models.Index(fields=['researcher_1', 'researcher_2']),
            models.Index(fields=['last_collaborated']),
        ]

    def __str__(self):
        return f"{self.researcher_1.user.get_full_name()} ↔ {self.researcher_2.user.get_full_name()}"


class Authorship(models.Model):
    """
    Intermediary model representing authorship relationship between a Researcher and Publication.
    Stores metadata about the authorship edge (author order).
    """
    researcher = models.ForeignKey(
        Researcher,
        on_delete=models.CASCADE,
        related_name='authorships'
    )
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='authorships'
    )
    order = models.IntegerField(
        help_text="Author order (1 for first author, 2 for second, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Authorship"
        verbose_name_plural = "Authorships"
        unique_together = ('researcher', 'publication')
        ordering = ['publication', 'order']
        indexes = [
            models.Index(fields=['publication', 'order']),
            models.Index(fields=['researcher', 'publication']),
        ]

    def __str__(self):
        return f"{self.researcher.user.get_full_name()} - {self.publication.title[:50]} (Order: {self.order})"
