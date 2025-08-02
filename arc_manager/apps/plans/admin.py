# apps/plans/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import Plan, Subscription, UpgradeRequest, Payment
import logging

logger = logging.getLogger(__name__)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'price', 'max_users', 'trial_days', 'billing_cycle_days', 'grace_period_days', 'is_active')
    list_filter = ('is_active', 'name')
    search_fields = ('name', 'display_name')
    ordering = ('price',)
    fieldsets = (
        ('Información Principal', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Configuración del Plan', {
            'fields': ('price', 'max_users', 'trial_days', 'billing_cycle_days', 'grace_period_days')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_method', 'amount', 'status', 'created_at', 'description', 'days_added', 'old_end_date', 'new_end_date')
    can_delete = False
    ordering = ('-created_at',)

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan', 'subscription_status', 'end_date_formatted', 'days_remaining_display', 'is_active')
    list_filter = ('subscription_status', 'plan__name')
    search_fields = ('organization__name', 'plan__display_name')
    list_select_related = ('organization', 'plan')
    
    # Define los campos que siempre deben ser de solo lectura.
    readonly_fields = ('start_date', 'grace_end_date', 'created_at', 'updated_at', 'days_remaining_display')
    
    # Define los fieldsets para las vistas de agregar y cambiar.
    add_fieldsets = (
        ("Información General", {
            'fields': ('organization', 'plan', 'subscription_status')
        }),
        ("Fechas Clave (se autocalculan)", {
            'fields': ('end_date',)
        }),
    )
    
    change_fieldsets = (
        ("Información General", {
            'fields': ('organization', 'plan', 'subscription_status')
        }),
        ("Fechas Clave", {
            'fields': ('start_date', 'end_date', 'grace_end_date', 'days_remaining_display')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [PaymentInline]
    actions = ['process_selected_payments']

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.change_fieldsets

    def get_readonly_fields(self, request, obj=None):
        # Si el objeto ya existe (vista de cambio), define campos de solo lectura específicos.
        if obj:
            # Permite la edición de 'plan' y 'end_date', pero mantiene el resto como solo lectura.
            return ('organization', 'subscription_status', 'start_date', 'grace_end_date', 'created_at', 'updated_at', 'days_remaining_display')
        
        # Para un objeto nuevo, usa la configuración estándar de solo lectura.
        return self.readonly_fields
    
    def add_view(self, request, form_url='', extra_context=None):
        # Precarga el ID de la organización desde el parámetro GET.
        # Esto asegura que el campo 'organization' se establezca correctamente.
        organization_id = request.GET.get('organization')
        if organization_id:
            # Inyecta el ID de la organización en los datos iniciales del formulario.
            request.GET = request.GET.copy()
            request.GET['organization'] = organization_id
            
        return super().add_view(request, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.update_status()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('plan', 'organization')

    @admin.display(description="Estado", ordering='subscription_status')
    def is_active(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Activa</span>')
        elif obj.is_in_grace_period:
            return format_html('<span style="color: orange;">● En Gracia</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">● Expirada</span>')
        return "Desconocido"

    @admin.display(description="Fecha de Vencimiento", ordering='end_date')
    def end_date_formatted(self, obj):
        if obj.end_date:
            return obj.end_date.strftime('%d de %b de %Y, %H:%M')
        return "N/A"

    @admin.display(description="Días Restantes")
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if obj.is_expired:
            return format_html('<span style="color: red;">Expirado</span>')
        if obj.is_in_grace_period:
            return format_html(f'<span style="color: orange;">{days} día(s) de gracia</span>')
        return f"{days} día(s)"

    @admin.action(description="💰 Procesar pago recibido y extender suscripción")
    def process_selected_payments(self, request, queryset):
        processed_count = 0
        for subscription in queryset:
            try:
                payment_result = subscription.process_payment(
                    amount=subscription.plan.price,
                    processed_by=request.user.username
                )
                
                # Limpiar la fecha de gracia explícitamente al procesar el pago
                subscription.grace_end_date = None
                subscription.save(update_fields=['grace_end_date'])

                if payment_result.get('success'):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error procesando pago para {subscription}: {e}")
                self.message_user(request, f"Error al procesar el pago para {subscription.organization.name}.", messages.ERROR)
        
        if processed_count > 0:
            self.message_user(request, f"{processed_count} suscripciones han sido extendidas exitosamente.", messages.SUCCESS)

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 'current_plan', 'requested_plan', 
        'amount', 'status_display', 'created_at', 'approved_by'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['organization__name']
    readonly_fields = [
        'organization', 'current_plan', 'requested_plan', 'amount',
        'created_at', 'updated_at', 'approved_by'
    ]
    ordering = ['-created_at']
    actions = ['approve_selected_requests']

    def status_display(self, obj):
        status_map = {
            'pending': ('orange', 'Pendiente'),
            'approved': ('green', 'Aprobado'),
            'rejected': ('red', 'Rechazado'),
        }
        color, text = status_map.get(obj.status, ('black', obj.get_status_display()))
        return format_html('<b style="color: {};">{}</b>', color, text)
    status_display.short_description = 'Estado'
    
    def approve_selected_requests(self, request, queryset):
        approved_count = 0
        for req in queryset.filter(status='pending'):
            result = req.approve(request.user)
            if result['success']:
                approved_count += 1
        self.message_user(request, f'{approved_count} solicitudes de upgrade aprobadas.', messages.SUCCESS)
    approve_selected_requests.short_description = "Aprobar solicitudes seleccionadas"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'subscription', 'amount', 'payment_method', 'payment_type', 'status', 
        'processed_by', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_type', 'created_at']
    search_fields = ['subscription__organization__name', 'processed_by']
    readonly_fields = [
        'subscription', 'amount', 'payment_method', 'payment_type', 'status',
        'processed_by', 'description', 'days_added', 'old_end_date',
        'new_end_date', 'created_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
        
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscription__organization')

admin.site.site_header = "ARC Manager - Administración"
admin.site.site_title = "ARC Manager Admin"
admin.site.index_title = "Panel de Administración"