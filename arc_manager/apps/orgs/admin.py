from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django import forms
from .models import Organization
from apps.plans.models import Plan, Subscription

class OrganizationPlanChangeForm(forms.ModelForm):
    """Formulario personalizado para cambiar plan desde el admin de organizaciones"""
    
    current_plan = forms.ModelChoiceField(
        queryset=Plan.objects.filter(is_active=True, price=0),  # Solo planes gratuitos
        required=False,
        label="Plan Actual (Solo Gratuitos/Trial)",
        help_text="Solo puedes cambiar a planes gratuitos o de prueba desde aquí. Para planes de pago, usa el sistema de solicitudes de upgrade."
    )
    
    class Meta:
        model = Organization
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si la organización existe, establecer el plan actual
            current_subscription = getattr(self.instance, 'subscription', None)
            if current_subscription:
                self.fields['current_plan'].initial = current_subscription.plan
            else:
                # Si no tiene suscripción, usar plan trial por defecto
                trial_plan = Plan.objects.filter(name='trial', is_active=True).first()
                if trial_plan:
                    self.fields['current_plan'].initial = trial_plan
                    
        # Mensaje de advertencia en el formulario
        self.fields['current_plan'].help_text += "\n⚠️ IMPORTANTE: Para cambiar a planes de pago, los usuarios deben usar el sistema de solicitudes de upgrade."
    
    def clean_current_plan(self):
        """Validar que solo se asignen planes gratuitos"""
        plan = self.cleaned_data.get('current_plan')
        if plan and plan.price > 0:
            raise forms.ValidationError(
                f"No puedes asignar directamente el plan '{plan.display_name}' (${plan.price}) desde el admin. "
                "Los planes de pago deben ser asignados a través del sistema de solicitudes de upgrade."
            )
        return plan
    
    def save(self, commit=True):
        instance = super().save(commit)
        
        if commit:
            # Gestionar la suscripción
            new_plan = self.cleaned_data.get('current_plan')
            if new_plan:
                subscription, created = Subscription.objects.get_or_create(
                    organization=instance,
                    defaults={'plan': new_plan}
                )
                
                if not created and subscription.plan != new_plan:
                    # Solo permitir cambio si el nuevo plan es gratuito
                    if new_plan.price > 0:
                        raise forms.ValidationError(
                            f"No se puede cambiar automáticamente a un plan de pago (${new_plan.price})"
                        )
                    
                    # Cambiar plan existente solo para planes gratuitos
                    old_plan = subscription.plan
                    subscription.plan = new_plan
                    
                    # Actualizar el status según el tipo de plan
                    if new_plan.name in ['gratuito', 'trial'] or new_plan.price == 0:
                        if new_plan.name == 'trial':
                            subscription.status = 'trial'
                            subscription.payment_status = 'pending'
                        else:
                            subscription.status = 'active'
                            subscription.payment_status = 'paid'  # Plan gratuito no requiere pago
                    
                    # Actualizar fechas si es necesario
                    subscription.setup_subscription_dates()
                    subscription.save()
                    
                    # Log del cambio
                    print(f"Plan cambiado para {instance.name}: {old_plan.display_name} → {new_plan.display_name} (Status: {subscription.status})")
        
        return instance

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    form = OrganizationPlanChangeForm
    list_display = ['name', 'is_active', 'get_active_user_count', 'get_user_count', 'get_subscription_info', 'user_limit_status', 'get_current_plan_display', 'created_at']
    list_filter = ['is_active', 'created_at', 'subscription__plan', 'subscription__status']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_user_count', 'get_active_user_count', 'get_inactive_user_count', 'user_limit_status', 'get_subscription_info', 'get_current_plan_info']
    
    # Acciones personalizadas
    actions = ['assign_trial_plan', 'assign_basic_plan', 'activate_organizations', 'deactivate_organizations']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Gestión de Plan (Solo Gratuitos)', {
            'fields': ('current_plan',),
            'description': '⚠️ IMPORTANTE: Aquí solo puedes asignar planes gratuitos o de prueba. Para planes de pago, los usuarios deben usar el sistema de "Solicitudes de Upgrade" donde se aprueban manualmente y se envían instrucciones de pago por correo.'
        }),
        ('Información de Suscripción (Solo Lectura)', {
            'fields': ('get_subscription_info', 'get_current_plan_info'),
            'description': 'Información sobre la suscripción activa y el plan actual',
            'classes': ('collapse',)
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
    
    def get_current_plan_display(self, obj):
        """Muestra el plan actual en la lista"""
        plan = obj.plan
        if plan:
            color = 'green' if plan.price == 0 else 'blue'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, plan.display_name
            )
        return format_html('<span style="color: red;">Sin plan</span>')
    get_current_plan_display.short_description = 'Plan Actual'
    
    def get_subscription_info(self, obj):
        """Muestra información de la suscripción"""
        if hasattr(obj, 'subscription'):
            subscription = obj.subscription
            status_color = {
                'trial': 'green',
                'active': 'blue', 
                'expired': 'red',
                'cancelled': 'gray'
            }.get(subscription.status, 'black')
            
            # Link directo para editar la suscripción
            subscription_url = reverse('admin:plans_subscription_change', args=[subscription.pk])
            
            return format_html(
                '<span style="color: {};">{}</span> - {} días restantes<br>'
                '<a href="{}" style="font-size: 0.9em;">📝 Editar suscripción</a>',
                status_color,
                subscription.get_status_display(),
                subscription.days_remaining,
                subscription_url
            )
        return format_html('<span style="color: red;">Sin suscripción</span>')
    get_subscription_info.short_description = 'Estado de Suscripción'
    
    def get_current_plan_info(self, obj):
        """Muestra información del plan actual"""
        plan = obj.plan
        if plan:
            plan_url = reverse('admin:plans_plan_change', args=[plan.pk])
            return format_html(
                '<strong><a href="{}">{}</a></strong><br>Usuarios: {}<br>Precio: ${}',
                plan_url,
                plan.display_name,
                plan.max_users,
                plan.price
            )
        return format_html('<span style="color: red;">Sin plan asignado</span>')
    get_current_plan_info.short_description = 'Plan Actual'
    
    def user_limit_status(self, obj):
        """Muestra el estado del límite de usuarios de forma visual"""
        limit_info = obj.can_add_user_detailed()
        
        if limit_info.get('subscription_issue', False):
            return format_html(
                '<span style="color: red;">🚫 {}</span>',
                limit_info['reason']
            )
        
        if limit_info['can_add']:
            return format_html(
                '<span style="color: green;">✅ Disponible ({} espacios libres)</span>',
                limit_info['available_slots']
            )
        else:
            return format_html(
                '<span style="color: red;">🚫 Límite alcanzado ({}/{})</span>',
                limit_info['total_users'],
                limit_info['max_users']
            )
    
    user_limit_status.short_description = 'Estado del Límite'
    
    # Acciones personalizadas
    def assign_trial_plan(self, request, queryset):
        """Asignar plan trial a organizaciones seleccionadas"""
        try:
            trial_plan = Plan.objects.get(name='trial', is_active=True)
        except Plan.DoesNotExist:
            self.message_user(request, "No se encontró un plan trial activo", messages.ERROR)
            return
        
        updated = 0
        for org in queryset:
            subscription, created = Subscription.objects.get_or_create(
                organization=org,
                defaults={'plan': trial_plan}
            )
            
            if not created:
                subscription.plan = trial_plan
                subscription.status = 'trial'
                subscription.save()
            
            updated += 1
        
        self.message_user(
            request, 
            f"Plan trial asignado a {updated} organizaciones",
            messages.SUCCESS
        )
    assign_trial_plan.short_description = "🆓 Asignar plan trial"
    
    def assign_basic_plan(self, request, queryset):
        """Asignar plan básico a organizaciones seleccionadas"""
        try:
            basic_plan = Plan.objects.get(name='basic', is_active=True)
        except Plan.DoesNotExist:
            self.message_user(request, "No se encontró un plan básico activo", messages.ERROR)
            return
        
        updated = 0
        for org in queryset:
            subscription, created = Subscription.objects.get_or_create(
                organization=org,
                defaults={'plan': basic_plan}
            )
            
            if not created:
                subscription.plan = basic_plan
                subscription.status = 'active'
                subscription.save()
            
            updated += 1
        
        self.message_user(
            request, 
            f"Plan básico asignado a {updated} organizaciones",
            messages.SUCCESS
        )
    assign_basic_plan.short_description = "💼 Asignar plan básico"
    
    def activate_organizations(self, request, queryset):
        """Activar organizaciones seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Se activaron {updated} organizaciones",
            messages.SUCCESS
        )
    activate_organizations.short_description = "✅ Activar organizaciones"
    
    def deactivate_organizations(self, request, queryset):
        """Desactivar organizaciones seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Se desactivaron {updated} organizaciones",
            messages.SUCCESS
        )
    deactivate_organizations.short_description = "❌ Desactivar organizaciones"
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado para mostrar mensaje de éxito"""
        super().save_model(request, obj, form, change)
        
        if change:
            # Si se cambió el plan, mostrar mensaje informativo
            new_plan = form.cleaned_data.get('current_plan')
            if new_plan:
                messages.success(
                    request,
                    f"Plan '{new_plan.display_name}' asignado correctamente a '{obj.name}'"
                )
