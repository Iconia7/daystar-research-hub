from django.contrib import admin
from .models import Researcher, Publication, Project, Thesis, Collaboration, Authorship


@admin.register(Researcher)
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'google_scholar_id', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'google_scholar_id', 'department')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Professional Details', {'fields': ('department', 'research_interests', 'google_scholar_id')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'doi', 'publication_date', 'created_at')
    list_filter = ('publication_date', 'created_at', 'sdg_tags')
    search_fields = ('title', 'doi', 'abstract')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Publication Details', {'fields': ('title', 'doi')}),
        ('Content', {'fields': ('abstract', 'publication_date')}),
        ('SDG Tags', {'fields': ('sdg_tags',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'funding_body', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'funding_body')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Project Details', {'fields': ('title', 'status')}),
        ('Funding & Timeline', {'fields': ('funding_body', 'start_date', 'end_date')}),
        ('Description', {'fields': ('description',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'thesis_type', 'supervisor', 'submission_date')
    list_filter = ('thesis_type', 'submission_date', 'created_at')
    search_fields = ('title', 'student', 'abstract')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Thesis Details', {'fields': ('title', 'thesis_type', 'student')}),
        ('Supervision', {'fields': ('supervisor',)}),
        ('Content', {'fields': ('abstract', 'submission_date')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('researcher_1', 'researcher_2', 'strength', 'last_collaborated')
    list_filter = ('last_collaborated', 'created_at')
    search_fields = ('researcher_1__user__first_name', 'researcher_1__user__last_name',
                     'researcher_2__user__first_name', 'researcher_2__user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Collaboration Parties', {'fields': ('researcher_1', 'researcher_2')}),
        ('Collaboration Metrics', {'fields': ('strength', 'last_collaborated')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Authorship)
class AuthorshipAdmin(admin.ModelAdmin):
    list_display = ('researcher', 'publication', 'order', 'created_at')
    list_filter = ('order', 'created_at')
    search_fields = ('researcher__user__first_name', 'researcher__user__last_name', 'publication__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Author & Publication', {'fields': ('researcher', 'publication')}),
        ('Author Order', {'fields': ('order',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
