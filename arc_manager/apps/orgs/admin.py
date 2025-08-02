from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'get_user_count', 'get_subscription_status', 'get_subscription_link', 'created_at']
    list_filter = ['is_active', 'created_at', 'subscription__plan', 'subscription__subscription_status']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_user_count', 'get_subscription_status', 'get_subscription_link']
    
    # Solo 2 acciones esenciales
    actions = ['activate_organizations', 'deactivate_organizations']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Suscripción', {
            'fields': ('get_subscription_status', 'get_subscription_link'),
            'description': '📝 Para gestionar planes y suscripciones, usa el módulo "Suscripciones" del admin.',
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('get_user_count',),
            'classes': ('collapse',)
        }),
        ('Información del sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_count(self, obj):
        """Muestra el total de usuarios"""
        return f"{obj.get_user_count()} usuarios"
    get_user_count.short_description = 'Usuarios'
    
    def get_subscription_status(self, obj):
        """Muestra el estado de la suscripción de forma simple y visual."""
        if hasattr(obj, 'subscription') and obj.subscription:
            subscription = obj.subscription
            plan = subscription.plan
            status_text = subscription.get_subscription_status_display()
            
            color = 'black'  # Color por defecto
            if subscription.is_active:
                color = 'green'
                if 'trial' in subscription.subscription_status:
                    color = '#E67E22'  # Naranja para trial
            elif subscription.is_in_grace_period:
                color = '#F39C12'  # Naranja más claro para periodo de gracia
            elif subscription.is_expired:
                color = '#E74C3C'  # Rojo para expirado

            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br>'
                '<small style="color: #555;">{} - {} días restantes</small>',
                color,
                status_text,
                plan.display_name,
                subscription.days_remaining
            )
        return format_html('<span style="color: #C0392B; font-weight: bold;">Sin suscripción</span>')
    get_subscription_status.short_description = 'Estado de Suscripción'
    
    def get_subscription_link(self, obj):
        """
        Proporciona un enlace para gestionar la suscripción existente o
        para crear una nueva si no existe.
        """
        if hasattr(obj, 'subscription') and obj.subscription:
            # Si la suscripción existe, enlace para editarla
            subscription_url = reverse('admin:plans_subscription_change', args=[obj.subscription.pk])
            return format_html('<a href="{}" class="button">📝 Gestionar suscripción</a>', subscription_url)
        else:
            # Si no hay suscripción, enlace para crear una nueva, pre-rellenando la organización
            add_subscription_url = reverse('admin:plans_subscription_add') + f'?organization={obj.pk}'
            return format_html('<a href="{}" class="button">➕ Crear suscripción</a>', add_subscription_url)
    get_subscription_link.short_description = 'Gestión'
    
    # Solo acciones esenciales para activar/desactivar
    def activate_organizations(self, request, queryset):
        """Activar organizaciones seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"✅ Se activaron {updated} organizaciones correctamente.",
            messages.SUCCESS
        )
    activate_organizations.short_description = "✅ Activar organizaciones"
    
    def deactivate_organizations(self, request, queryset):
        """Desactivar organizaciones seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"❌ Se desactivaron {updated} organizaciones correctamente.",
            messages.SUCCESS
        )
    deactivate_organizations.short_description = "❌ Desactivar organizaciones"
