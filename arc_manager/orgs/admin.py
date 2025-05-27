from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'get_user_count', 'max_users', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'get_user_count']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Configuración', {
            'fields': ('max_users',)
        }),
        ('Información del sistema', {
            'fields': ('created_at', 'updated_at', 'get_user_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_count(self, obj):
        return obj.get_user_count()
    get_user_count.short_description = 'Usuarios'
