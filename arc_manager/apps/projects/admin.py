from django.contrib import admin
from .models import Project, Task, ProjectFile

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'owner', 'phase', 'created_at')
    list_filter = ('phase', 'owner', 'created_at')
    search_fields = ('name', 'client', 'owner__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'completed', 'created_at')
    list_filter = ('completed', 'project__name', 'assigned_to')
    search_fields = ('title', 'project__name')
    ordering = ('-created_at',)

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'project', 'upload_phase', 'uploaded_at')
    list_filter = ('upload_phase', 'project__name')
    search_fields = ('file__name',)
    ordering = ('-uploaded_at',)
