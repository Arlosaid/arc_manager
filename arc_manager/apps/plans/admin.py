from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'max_users', 'price', 'is_active']
    list_filter = ['is_active', 'name']
    search_fields = ['display_name', 'name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Límites', {
            'fields': ('max_users', 'price')
        }),
        ('Estado', {
            'fields': ('is_active', 'created_at')
        }),
    )
