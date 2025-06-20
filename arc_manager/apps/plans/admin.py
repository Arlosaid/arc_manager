# apps/plans/admin.py (actualizado)
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from .models import Plan, Subscription, UpgradeRequest
import logging

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'name', 'price_display_admin', 'billing_cycle',
        'max_users', 'max_projects', 'storage_limit_gb',
        'is_active', 'is_featured', 'subscription_count', 'revenue_display'
    ]
    list_filter = ['is_active', 'is_featured', 'billing_cycle', 'name']
    search_fields = ['display_name', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'subscription_count', 'revenue_display']
    ordering = ['sort_order', 'price']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'display_name', 'description', 'sort_order')
        }),
        ('Precios y Facturación', {
            'fields': ('price', 'currency', 'billing_cycle', 'trial_days')
        }),
        ('Límites del Plan', {
            'fields': ('max_users', 'max_projects', 'storage_limit_gb')
        }),
        ('Características', {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        ('Estado y Configuración', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Integración con Stripe', {
            'fields': ('stripe_product_id', 'stripe_price_id'),
            'classes': ('collapse',),
            'description': 'Para integración futura con Stripe'
        }),
        ('Estadísticas', {
            'fields': ('subscription_count', 'revenue_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display_admin(self, obj):
        """Muestra el precio formateado en el admin"""
        if obj.price == 0:
            return format_html('<span style="color: green; font-weight: bold;">Gratis</span>')
        return f"${obj.price:,.0f} {obj.currency}"
    price_display_admin.short_description = 'Precio'
    
    def subscription_count(self, obj):
        """Cuenta las suscripciones activas del plan"""
        count = obj.subscription_set.filter(status__in=['active', 'trial']).count()
        if count > 0:
            url = reverse('admin:plans_subscription_changelist') + f'?plan__id__exact={obj.id}'
            return format_html('<a href="{}">{} suscripciones</a>', url, count)
        return '0 suscripciones'
    subscription_count.short_description = 'Suscripciones Activas'
    
    def revenue_display(self, obj):
        """Muestra los ingresos mensuales estimados"""
        revenue = obj.total_monthly_revenue
        if revenue > 0:
            revenue_formatted = f"${revenue:,.0f}/mes"
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', revenue_formatted)
        return '$0/mes'
    revenue_display.short_description = 'Ingresos Mensuales'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subscription_set')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'organization_link', 'plan_link', 'status_display', 'payment_status_display',
        'start_date', 'end_date', 'days_remaining_display', 'last_payment_date', 'user_count_display'
    ]
    list_filter = [
        'status', 'payment_status', 'plan__name', 'plan__billing_cycle',
        'auto_renew', 'cancel_at_period_end', 'created_at'
    ]
    search_fields = [
        'organization__name', 'organization__slug',
        'plan__display_name', 'plan__name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'days_remaining_display',
        'trial_days_remaining_display', 'is_active_display', 'user_count_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    # Acciones personalizadas para gestión manual
    actions = [
        'activate_subscriptions', 
        'extend_trial_30_days', 
        'extend_subscription_1_month',
        'extend_subscription_3_months',
        'mark_payment_received',
        'apply_basic_plan',
        'apply_trial_plan',
        'check_status'
    ]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('organization', 'plan', 'status', 'payment_status'),
            'description': 'Información básica de la suscripción'
        }),
        ('Fechas', {
            'fields': (
                'start_date', 'end_date', 'trial_end_date',
                'last_payment_date', 'next_billing_date'
            ),
            'description': 'Gestión de fechas importantes'
        }),
        ('Configuración', {
            'fields': ('auto_renew', 'cancel_at_period_end'),
            'description': 'Configuración de renovación automática'
        }),
        ('Gestión Manual de Pagos (MVP)', {
            'fields': (),
            'description': 'Usa las acciones en lote para gestionar pagos manuales: marcar pagos recibidos, extender suscripciones, cambiar planes.'
        }),
        ('Integración con Stripe (Futuro)', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Metadatos y Notas', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Información adicional y historial de pagos manuales'
        }),
        ('Estado Calculado', {
            'fields': (
                'is_active_display', 'days_remaining_display',
                'trial_days_remaining_display', 'user_count_display'
            ),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def organization_link(self, obj):
        """Link a la organización"""
        url = reverse('admin:orgs_organization_change', args=[obj.organization.pk])
        return format_html('<a href="{}">{}</a>', url, obj.organization.name)
    organization_link.short_description = 'Organización'
    
    def plan_link(self, obj):
        """Link al plan"""
        url = reverse('admin:plans_plan_change', args=[obj.plan.pk])
        color = 'green' if obj.plan.price == 0 else 'blue'
        return format_html('<a href="{}" style="color: {};">{}</a>', url, color, obj.plan.display_name)
    plan_link.short_description = 'Plan'
    
    def status_display(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'active': 'green',
            'trial': 'orange',
            'expired': 'red',
            'cancelled': 'red',
            'suspended': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'
    
    def payment_status_display(self, obj):
        """Muestra el estado de pago con colores"""
        colors = {
            'paid': 'green',
            'pending': 'orange',
            'failed': 'red',
            'cancelled': 'red'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Estado de Pago'
    
    def days_remaining_display(self, obj):
        """Muestra los días restantes con colores según urgencia"""
        days = obj.days_remaining
        if days <= 0:
            color = 'red'
            text = 'Expirado'
        elif days <= 3:
            color = 'red'
            text = f'{days} días'
        elif days <= 7:
            color = 'orange'
            text = f'{days} días'
        else:
            color = 'green'
            text = f'{days} días'
        
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    days_remaining_display.short_description = 'Días Restantes'
    
    def trial_days_remaining_display(self, obj):
        """Muestra los días restantes del trial"""
        if not obj.is_trial:
            return 'N/A'
        
        days = obj.trial_days_remaining
        if days <= 0:
            return format_html('<span style="color: red;">Trial expirado</span>')
        
        color = 'orange' if days <= 7 else 'green'
        return format_html('<span style="color: {};">{} días de trial</span>', color, days)
    trial_days_remaining_display.short_description = 'Trial Restante'
    
    def is_active_display(self, obj):
        """Muestra si la suscripción está activa"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Activa</span>')
        return format_html('<span style="color: red;">✗ Inactiva</span>')
    is_active_display.short_description = 'Estado Activo'
    
    def user_count_display(self, obj):
        """Muestra el conteo de usuarios de la organización"""
        count = obj.organization.get_user_count()
        limit = obj.plan.max_users
        percentage = (count / limit * 100) if limit > 0 else 0
        
        if percentage >= 100:
            color = 'red'
        elif percentage >= 80:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color: {};">{}/{} usuarios ({}%)</span>',
            color, count, limit, int(percentage)
        )
    user_count_display.short_description = 'Usuarios'
    
    # Acciones personalizadas para gestión manual
    def activate_subscriptions(self, request, queryset):
        """Activar suscripciones seleccionadas"""
        updated = 0
        for subscription in queryset:
            if subscription.status != 'active':
                subscription.status = 'active'
                subscription.payment_status = 'paid'
                subscription.save()
                updated += 1
        
        self.message_user(
            request,
            f"Se activaron {updated} suscripciones correctamente.",
            messages.SUCCESS
        )
    activate_subscriptions.short_description = "✅ Activar suscripciones"
    
    def extend_trial_30_days(self, request, queryset):
        """Extender trial por 30 días"""
        updated = 0
        for subscription in queryset:
            subscription.extend_subscription(days=30)
            updated += 1
        
        self.message_user(
            request,
            f"Se extendieron {updated} suscripciones por 30 días.",
            messages.SUCCESS
        )
    extend_trial_30_days.short_description = "⏰ Extender 30 días"
    
    def extend_subscription_1_month(self, request, queryset):
        """Extender suscripción por 1 mes (pago recibido)"""
        updated = 0
        for subscription in queryset:
            subscription.extend_subscription(days=30)
            subscription.payment_status = 'paid'
            subscription.last_payment_date = timezone.now()
            
            # Agregar al historial de pagos
            if not subscription.metadata:
                subscription.metadata = {}
            
            payment_history = subscription.metadata.get('payment_history', [])
            payment_history.append({
                'date': timezone.now().isoformat(),
                'amount': float(subscription.plan.price),
                'method': 'manual',
                'status': 'paid',
                'note': f'Pago manual procesado por {request.user.username}'
            })
            subscription.metadata['payment_history'] = payment_history
            subscription.save()
            updated += 1
        
        self.message_user(
            request,
            f"Se procesaron {updated} pagos y se extendieron las suscripciones por 1 mes.",
            messages.SUCCESS
        )
    extend_subscription_1_month.short_description = "💰 Procesar pago (1 mes)"
    
    def extend_subscription_3_months(self, request, queryset):
        """Extender suscripción por 3 meses (pago anual o trimestral)"""
        updated = 0
        for subscription in queryset:
            subscription.extend_subscription(days=90)
            subscription.payment_status = 'paid'
            subscription.last_payment_date = timezone.now()
            
            # Agregar al historial de pagos
            if not subscription.metadata:
                subscription.metadata = {}
            
            payment_history = subscription.metadata.get('payment_history', [])
            payment_history.append({
                'date': timezone.now().isoformat(),
                'amount': float(subscription.plan.price * 3),
                'method': 'manual',
                'status': 'paid',
                'note': f'Pago trimestral manual procesado por {request.user.username}'
            })
            subscription.metadata['payment_history'] = payment_history
            subscription.save()
            updated += 1
        
        self.message_user(
            request,
            f"Se procesaron {updated} pagos trimestrales y se extendieron las suscripciones por 3 meses.",
            messages.SUCCESS
        )
    extend_subscription_3_months.short_description = "💎 Procesar pago (3 meses)"
    
    def mark_payment_received(self, request, queryset):
        """Marcar pago como recibido sin extender"""
        updated = 0
        for subscription in queryset:
            subscription.payment_status = 'paid'
            subscription.last_payment_date = timezone.now()
            subscription.save()
            updated += 1
        
        self.message_user(
            request,
            f"Se marcaron {updated} pagos como recibidos.",
            messages.SUCCESS
        )
    mark_payment_received.short_description = "✅ Marcar pago recibido"
    
    def apply_basic_plan(self, request, queryset):
        """Aplicar plan básico a las organizaciones seleccionadas"""
        try:
            basic_plan = Plan.objects.get(name='basic', is_active=True)
        except Plan.DoesNotExist:
            self.message_user(
                request,
                "No se encontró un plan básico activo.",
                messages.ERROR
            )
            return
        
        updated = 0
        for subscription in queryset:
            subscription.plan = basic_plan
            subscription.status = 'active'
            subscription.payment_status = 'paid'
            subscription.save()
            updated += 1
        
        self.message_user(
            request,
            f"Se aplicó el plan básico a {updated} organizaciones.",
            messages.SUCCESS
        )
    apply_basic_plan.short_description = "🔄 Aplicar plan básico"
    
    def apply_trial_plan(self, request, queryset):
        """Aplicar plan de prueba a las organizaciones seleccionadas"""
        try:
            trial_plan = Plan.objects.get(name='trial', is_active=True)
        except Plan.DoesNotExist:
            self.message_user(
                request,
                "No se encontró un plan de prueba activo.",
                messages.ERROR
            )
            return
        
        updated = 0
        for subscription in queryset:
            subscription.plan = trial_plan
            subscription.status = 'trial'
            subscription.payment_status = 'pending'
            subscription.end_date = timezone.now() + timedelta(days=trial_plan.trial_days)
            subscription.save()
            updated += 1
        
        self.message_user(
            request,
            f"Se aplicó el plan de prueba a {updated} organizaciones.",
            messages.SUCCESS
        )
    apply_trial_plan.short_description = "🆓 Aplicar plan trial"
    
    def check_status(self, request, queryset):
        """Verificar y actualizar estado de suscripciones"""
        updated = 0
        for subscription in queryset:
            old_status = subscription.status
            subscription.check_and_update_status()
            if subscription.status != old_status:
                updated += 1
        
        self.message_user(
            request,
            f"Se actualizaron {updated} estados de suscripción.",
            messages.SUCCESS
        )
    check_status.short_description = "🔄 Verificar estados"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization', 'plan')

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    list_display = [
        'organization_name', 'current_plan_name', 'requested_plan_name', 
        'status_display', 'amount_due', 'requested_date', 'requested_by_link'
    ]
    
    list_filter = [
        'status', 'requested_date', 'current_plan__name', 'requested_plan__name'
    ]
    
    search_fields = [
        'organization__name', 'organization__slug', 
        'requested_by__email', 'requested_by__first_name', 'requested_by__last_name'
    ]
    
    readonly_fields = [
        'organization_link', 'requested_by_link', 'requested_date', 
        'approved_date', 'price_difference_display', 'status_help_text'
    ]
    
    actions = ['approve_requests', 'reject_requests']
    
    fieldsets = (
        ('🚨 ACCIONES RÁPIDAS', {
            'fields': ('status', 'status_help_text'),
            'description': '⚡ Cambio rápido de estado con acciones automáticas',
            'classes': ('wide',)
        }),
        ('📋 Información de la Solicitud', {
            'fields': (
                'organization_link', 'requested_by_link',
                'requested_date', 'approved_date'
            ),
            'description': 'Información básica de la solicitud'
        }),
        ('💰 Detalles del Upgrade', {
            'fields': (
                'current_plan', 'requested_plan', 
                'amount_due', 'price_difference_display'
            ),
            'description': 'Información de los planes y costos'
        }),
        ('📝 Notas y Comentarios', {
            'fields': (
                'request_notes', 'admin_notes', 'rejection_reason'
            ),
            'description': 'Comentarios y notas del proceso'
        }),
        ('👥 Usuarios Involucrados', {
            'fields': ('requested_by', 'approved_by'),
            'classes': ('collapse',)
        }),
        ('📞 Información de Contacto', {
            'fields': ('contact_info',),
            'classes': ('collapse',)
        }),
    )
    
    def organization_name(self, obj):
        """Nombre de la organización"""
        return obj.organization.name
    organization_name.short_description = 'Organización'
    
    def current_plan_name(self, obj):
        """Nombre del plan actual"""
        return obj.current_plan.display_name
    current_plan_name.short_description = 'Plan Actual'
    
    def requested_plan_name(self, obj):
        """Nombre del plan solicitado"""
        return format_html(
            '<strong style="color: blue;">{}</strong>',
            obj.requested_plan.display_name
        )
    requested_plan_name.short_description = 'Plan Solicitado'
    
    def requested_by_link(self, obj):
        """Link al usuario que solicitó"""
        url = reverse('admin:accounts_user_change', args=[obj.requested_by.pk])
        return format_html('<a href="{}">{}</a>', url, obj.requested_by.get_full_name() or obj.requested_by.email)
    requested_by_link.short_description = 'Solicitado por'
    
    def status_display(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'
    
    def price_difference_display(self, obj):
        """Muestra la diferencia de precio"""
        diff = obj.price_difference
        return format_html(
            '<span style="color: green; font-weight: bold;">+${}</span>',
            diff
        )
    price_difference_display.short_description = 'Diferencia de Precio'
    
    def status_help_text(self, obj):
        """Muestra ayuda sobre los estados"""
        help_texts = {
            'pending': '🟠 Pendiente: El usuario ya recibió instrucciones de pago. Cambiar a "Aprobada" cuando confirme el pago.',
            'approved': '🟢 Aprobada: El upgrade fue aplicado y el usuario notificado.',
            'rejected': '🔴 Rechazada: La solicitud fue denegada.',
            'cancelled': '⚫ Cancelada: La solicitud fue cancelada.'
        }
        
        current_help = help_texts.get(obj.status, '')
        
        # Agregar pasos siguientes
        if obj.status == 'pending':
            current_help += '<br><strong>📧 Acción:</strong> Cuando recibas el comprobante de pago, cambia a "Aprobada"'
        elif obj.status == 'approved':
            current_help += '<br><strong>✅ Completado:</strong> El plan está activo y el usuario fue notificado'
        elif obj.status in ['rejected', 'cancelled']:
            current_help += '<br><strong>🔚 Estado final:</strong> Proceso terminado'
        
        return format_html(current_help)
    status_help_text.short_description = 'Guía de Estados'
    
    def organization_link(self, obj):
        """Link a la organización"""
        url = reverse('admin:orgs_organization_change', args=[obj.organization.pk])
        return format_html('<a href="{}">{}</a>', url, obj.organization.name)
    organization_link.short_description = 'Ver Organización'
    
    # Acciones simplificadas
    def approve_requests(self, request, queryset):
        """Aprobar solicitudes seleccionadas"""
        approved_count = 0
        for upgrade_request in queryset.filter(status='pending'):
            try:
                upgrade_request.approve(
                    approved_by_user=request.user,
                    admin_notes=f"Aprobado por {request.user.username} desde el admin"
                )
                approved_count += 1
            except Exception as e:
                # Log detallado del error para desarrolladores
                logger = logging.getLogger(__name__)
                logger.error(f"Error al aprobar solicitud de {upgrade_request.organization.name}: {str(e)}", exc_info=True)
                
                # Siempre mostrar mensaje amigable, nunca errores técnicos
                messages.error(
                    request,
                    "❌ Error al aprobar solicitud. Por favor, contacta con soporte técnico."
                )
        
        if approved_count > 0:
            self.message_user(
                request,
                f"✅ Se aprobaron {approved_count} solicitudes. Los planes fueron actualizados y los usuarios notificados.",
                messages.SUCCESS
            )
    approve_requests.short_description = "✅ Aprobar solicitudes seleccionadas"
    
    def reject_requests(self, request, queryset):
        """Rechazar solicitudes seleccionadas"""
        rejected_count = 0
        for upgrade_request in queryset.filter(status='pending'):
            try:
                upgrade_request.reject(
                    rejected_by_user=request.user,
                    reason="Rechazado desde el panel de administración"
                )
                rejected_count += 1
            except Exception as e:
                # Log detallado del error para desarrolladores
                logger = logging.getLogger(__name__)
                logger.error(f"Error al rechazar solicitud de {upgrade_request.organization.name}: {str(e)}", exc_info=True)
                
                # Siempre mostrar mensaje amigable, nunca errores técnicos
                self.message_user(
                    request,
                    "❌ Error al rechazar solicitud. Por favor, contacta con soporte técnico.",
                    messages.ERROR
                )
        
        if rejected_count > 0:
            self.message_user(
                request,
                f"❌ Se rechazaron {rejected_count} solicitudes. Los usuarios fueron notificados.",
                messages.SUCCESS
            )
    reject_requests.short_description = "❌ Rechazar solicitudes seleccionadas"
    
    def save_model(self, request, obj, form, change):
        """Manejar cambios de estado cuando se edita individualmente"""
        original_status = None
        
        if change and obj.pk:
            # Obtener el estado original de la base de datos
            try:
                original_obj = UpgradeRequest.objects.get(pk=obj.pk)
                original_status = original_obj.status
            except UpgradeRequest.DoesNotExist:
                original_status = 'pending'
        
        new_status = obj.status
        
        # Guardar el objeto primero
        super().save_model(request, obj, form, change)
        
        # Ejecutar acciones post-guardado
        if change and original_status and original_status != new_status:
            try:
                if new_status == 'approved' and original_status == 'pending':
                    # Aprobar la solicitud
                    obj.approve(
                        approved_by_user=request.user,
                        admin_notes=f"Aprobado por {request.user.username} desde el admin"
                    )
                    messages.success(
                        request,
                        f"✅ Solicitud aprobada. {obj.organization.name} ahora tiene el plan {obj.requested_plan.display_name}."
                    )
                    
                elif new_status == 'rejected' and original_status == 'pending':
                    # Rechazar la solicitud
                    obj.reject(
                        rejected_by_user=request.user,
                        reason="Rechazado desde el panel de administración"
                    )
                    messages.warning(
                        request,
                        f"❌ Solicitud rechazada. Se notificó a {obj.organization.name}."
                    )
                    
            except Exception as e:
                # Log detallado del error para desarrolladores
                logger = logging.getLogger(__name__)
                logger.error(f"Error al procesar cambio de estado: {str(e)}", exc_info=True)
                
                # Siempre mostrar mensaje amigable, nunca errores técnicos
                messages.error(
                    request,
                    "❌ Error al procesar el cambio de estado. Por favor, contacta con soporte técnico."
                )

# Configuración adicional del admin
admin.site.site_header = "ARC Manager - Administración"
admin.site.site_title = "ARC Manager Admin"
admin.site.index_title = "Panel de Administración"