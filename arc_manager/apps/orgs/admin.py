from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'get_active_user_count', 'get_inactive_user_count', 'get_user_count', 'max_users', 'user_limit_status', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'get_user_count', 'get_active_user_count', 'get_inactive_user_count', 'user_limit_status']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Configuración', {
            'fields': ('max_users',),
            'description': 'Límite total de usuarios (activos e inactivos)'
        }),
        ('Estadísticas de usuarios', {
            'fields': ('get_active_user_count', 'get_inactive_user_count', 'get_user_count', 'user_limit_status'),
            'classes': ('collapse',)
        }),
        ('Información del sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_active_user_count(self, obj):
        return obj.get_active_user_count()
    get_active_user_count.short_description = 'Usuarios Activos'
    
    def get_inactive_user_count(self, obj):
        return obj.get_inactive_user_count()
    get_inactive_user_count.short_description = 'Usuarios Inactivos'
    
    def get_user_count(self, obj):
        return obj.get_user_count()
    get_user_count.short_description = 'Total Usuarios'
    
    def user_limit_status(self, obj):
        """Muestra el estado del límite de usuarios de forma visual"""
        limit_info = obj.can_add_user_detailed()
        
        if limit_info['can_add']:
            return f"✅ Disponible ({limit_info['available_slots']} espacios libres)"
        else:
            return f"🚫 Límite alcanzado ({limit_info['total_users']}/{limit_info['max_users']})"
    
    user_limit_status.short_description = 'Estado del Límite'
