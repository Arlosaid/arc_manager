# apps/plans/views.py (actualizado)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from django.db import models
from datetime import timedelta

from .models import Plan, Subscription, UpgradeRequest
from .services import SubscriptionService
from apps.orgs.models import Organization


# Mixins para verificación de permisos
class OrgAdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere ser admin de organización"""
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_org_admin
    
    def handle_no_permission(self):
        messages.error(self.request, "Necesitas permisos de administrador de organización.")
        return redirect('main:home')


# Formularios
class PlanForm(forms.ModelForm):
    """Formulario para crear/editar planes"""
    
    class Meta:
        model = Plan
        fields = [
            'name', 'display_name', 'description', 'price', 'currency', 
            'billing_cycle', 'max_users', 'max_projects', 'storage_limit_gb',
            'trial_days', 'features', 'is_active', 'is_featured', 'sort_order'
        ]
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-control'}),
            'max_users': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_projects': forms.NumberInput(attrs={'class': 'form-control'}),
            'storage_limit_gb': forms.NumberInput(attrs={'class': 'form-control'}),
            'trial_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'features': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': '{"features": ["Característica 1", "Característica 2"]}'
            }),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Vistas públicas
class PublicPricingView(TemplateView):
    """Vista pública de precios para visitantes"""
    template_name = 'plans/public_pricing.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener planes activos ordenados
        context['plans'] = Plan.objects.filter(
            is_active=True
        ).order_by('sort_order', 'price')
        
        # Plan destacado
        context['featured_plan'] = Plan.objects.filter(
            is_featured=True,
            is_active=True
        ).first()
        
        # Estadísticas para mostrar credibilidad
        context['stats'] = {
            'total_organizations': Organization.objects.count(),
            'total_users': Organization.objects.filter(users__isnull=False).count(),
        }
        
        return context


# Vistas para usuarios autenticados
class SubscriptionDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de suscripción para organizaciones - Vista mejorada para MVP"""
    template_name = 'plans/subscription_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        # Verificar que el usuario tenga organización
        if not hasattr(user, 'organization') or not user.organization:
            context['no_organization'] = True
            context['is_org_admin'] = user.is_org_admin if hasattr(user, 'is_org_admin') else False
            return context
        
        organization = user.organization
        
        # Obtener o crear suscripción
        subscription, created = Subscription.objects.get_or_create(
            organization=organization,
            defaults={'plan': Plan.get_trial_plan() or Plan.objects.filter(is_active=True).first()}
        )
        
        if created:
            messages.info(
                self.request,
                "Se ha creado tu periodo de prueba gratuito. ¡Bienvenido!"
            )
        
        context['subscription'] = subscription
        context['organization'] = organization
        context['current_plan'] = subscription.plan
        context['is_org_admin'] = user.is_org_admin if hasattr(user, 'is_org_admin') else False
        
        # Estadísticas de uso detalladas
        user_count = organization.get_user_count()
        context['usage_stats'] = {
            'users': {
                'current': user_count,
                'limit': subscription.plan.max_users,
                'percentage': subscription.plan.get_usage_percentage(user_count, 'users'),
                'available': max(0, subscription.plan.max_users - user_count),
                'can_add': organization.can_add_user(),
                'is_at_limit': user_count >= subscription.plan.max_users
            },
            'projects': {
                'current': 0,  # TODO: implementar cuando tengas el módulo de proyectos
                'limit': subscription.plan.max_projects,
                'percentage': 0,
                'available': subscription.plan.max_projects,
                'can_add': True
            },
            'storage': {
                'current': 0,  # TODO: implementar cuando tengas almacenamiento
                'current_gb': 0,
                'limit': subscription.plan.storage_limit_gb,
                'percentage': 0,
                'available_gb': subscription.plan.storage_limit_gb,
                'can_upload': True
            }
        }
        
        # Estado de la suscripción con alertas
        days_remaining = subscription.days_remaining
        context['subscription_status'] = {
            'is_active': subscription.is_active,
            'is_trial': subscription.is_trial,
            'days_remaining': days_remaining,
            'trial_days_remaining': subscription.trial_days_remaining if subscription.is_trial else 0,
            'expires_soon': days_remaining <= 7 and days_remaining > 0,
            'is_expired': days_remaining <= 0,
            'needs_payment': subscription.payment_status == 'pending',
            'next_billing_date': subscription.next_billing_date,
            'status_display': subscription.get_status_display(),
            'payment_status_display': subscription.get_payment_status_display()
        }
        
        # Planes disponibles para upgrade (solo para admins de org)
        if context['is_org_admin']:
            context['available_plans'] = Plan.objects.filter(
                is_active=True,
                price__gt=subscription.plan.price
            ).order_by('price')
        
        # Historial de pagos simplificado (últimos 5)
        payment_history = []
        if subscription.metadata and subscription.metadata.get('payment_history'):
            payment_history = subscription.metadata['payment_history'][-5:]
            payment_history.reverse()  # Más recientes primero
        context['payment_history'] = payment_history
        
        # Características del plan actual
        context['plan_features'] = subscription.plan.get_feature_list()
        
        # Información de contacto para soporte
        context['support_info'] = {
            'email': 'soporte@tudominio.com',
            'phone': '+52 55 1234 5678',
            'hours': 'Lunes a Viernes 9:00 - 18:00'
        }
        
        # Alertas y notificaciones
        alerts = []
        
        if subscription.is_trial and subscription.trial_days_remaining <= 7:
            alerts.append({
                'type': 'warning',
                'title': 'Período de prueba próximo a vencer',
                'message': f'Tu período de prueba vence en {subscription.trial_days_remaining} días. Contacta con nosotros para continuar con un plan de pago.',
                'action': 'upgrade'
            })
        
        if days_remaining <= 3 and days_remaining > 0:
            alerts.append({
                'type': 'danger',
                'title': 'Suscripción próxima a vencer',
                'message': f'Tu suscripción vence en {days_remaining} días. Realiza tu pago para continuar sin interrupciones.',
                'action': 'payment'
            })
        
        if days_remaining <= 0:
            alerts.append({
                'type': 'danger',
                'title': 'Suscripción expirada',
                'message': 'Tu suscripción ha expirado. Contacta con nosotros para reactivar tu servicio.',
                'action': 'contact'
            })
        
        if context['usage_stats']['users']['percentage'] >= 90:
            alerts.append({
                'type': 'info',
                'title': 'Límite de usuarios próximo',
                'message': f'Has usado {context["usage_stats"]["users"]["current"]} de {context["usage_stats"]["users"]["limit"]} usuarios disponibles. Considera actualizar tu plan.',
                'action': 'upgrade'
            })
        
        context['alerts'] = alerts
        
        # Métodos de pago disponibles
        context['payment_methods'] = [
            {
                'name': 'Transferencia Bancaria',
                'icon': 'fas fa-university',
                'description': 'Transferencia a nuestra cuenta bancaria',
                'processing_time': '1-2 días hábiles'
            },
            {
                'name': 'Depósito en Efectivo',
                'icon': 'fas fa-money-bill-wave',
                'description': 'Depósito en sucursal bancaria',
                'processing_time': '1-2 días hábiles'
            }
        ]
        
        return context




# Vistas de superusuario
# Las vistas de superuser han sido eliminadas - toda la gestión se hace desde el admin de Django





# Funciones auxiliares y API


@login_required
def check_subscription_limits(request):
    """API para verificar límites de suscripción"""
    user = request.user
    organization = getattr(user, 'organization', None)
    
    if not organization:
        return JsonResponse({
            'success': False,
            'error': 'No hay organización asociada'
        })
    
    subscription = getattr(organization, 'subscription', None)
    if not subscription:
        return JsonResponse({
            'success': False,
            'error': 'No hay suscripción activa'
        })
    
    limit_type = request.GET.get('type', 'users')
    current_count = int(request.GET.get('current', 0))
    
    result = SubscriptionService.check_subscription_limits(
        organization,
        limit_type,
        current_count
    )
    
    return JsonResponse(result)


def plan_pricing_redirect(request):
    """Redirige según el tipo de usuario"""
    user = request.user
    
    if not user.is_authenticated:
        return redirect('plans:pricing')
    
    # Los superusers son redirigidos al admin de Django
    if user.is_superuser:
        return redirect('/admin/')
    elif hasattr(user, 'organization') and user.organization and user.is_org_admin:
        return redirect('main:dashboard')
    else:
        return redirect('plans:pricing')


# Las vistas de gestión de superuser han sido eliminadas - toda la gestión se hace desde el admin de Django


class RequestUpgradeView(LoginRequiredMixin, OrgAdminRequiredMixin, TemplateView):
    """Vista para que usuarios soliciten upgrade de plan"""
    template_name = 'plans/request_upgrade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        organization = user.organization
        
        if not organization:
            context['no_organization'] = True
            return context
        
        # Obtener suscripción actual
        subscription = get_object_or_404(Subscription, organization=organization)
        
        # Verificar si ya hay un request pendiente
        pending_request = UpgradeRequest.objects.filter(
            organization=organization,
            status__in=['pending', 'approved', 'payment_pending']
        ).first()
        
        if pending_request:
            context['has_pending_request'] = True
            context['pending_request'] = pending_request
        else:
            context['has_pending_request'] = False
            # Planes disponibles para upgrade
            context['available_plans'] = Plan.objects.filter(
                is_active=True,
                price__gt=subscription.plan.price
            ).order_by('price')
        
        context['subscription'] = subscription
        context['current_plan'] = subscription.plan
        context['organization'] = organization
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar solicitud de upgrade"""
        user = request.user
        organization = user.organization
        
        if not organization:
            messages.error(request, "No tienes una organización asignada.")
            return redirect('plans:subscription_dashboard')
        
        subscription = get_object_or_404(Subscription, organization=organization)
        
        # Verificar si ya hay un request pendiente
        if UpgradeRequest.objects.filter(
            organization=organization,
            status__in=['pending', 'approved', 'payment_pending']
        ).exists():
            messages.warning(request, "Ya tienes una solicitud de upgrade pendiente.")
            return redirect('plans:request_upgrade')
        
        # Obtener plan solicitado
        requested_plan_id = request.POST.get('requested_plan')
        if not requested_plan_id:
            messages.error(request, "Debes seleccionar un plan.")
            return redirect('plans:request_upgrade')
        
        requested_plan = get_object_or_404(Plan, id=requested_plan_id, is_active=True)
        
        # Verificar que sea un upgrade válido
        if requested_plan.price <= subscription.plan.price:
            messages.error(request, "Solo puedes hacer upgrade a un plan superior.")
            return redirect('plans:request_upgrade')
        
        # Crear solicitud de upgrade
        try:
            with transaction.atomic():
                upgrade_request = UpgradeRequest.objects.create(
                    organization=organization,
                    current_plan=subscription.plan,
                    requested_plan=requested_plan,
                    requested_by=user,
                    amount_due=requested_plan.price - subscription.plan.price,
                    request_notes=request.POST.get('notes', ''),
                    contact_info={
                        'email': user.email,
                        'phone': request.POST.get('phone', ''),
                        'preferred_contact': request.POST.get('preferred_contact', 'email')
                    }
                )
                
                messages.success(
                    request, 
                    f"Tu solicitud de upgrade a {requested_plan.display_name} ha sido enviada. "
                    "Recibirás una notificación cuando sea revisada por nuestro equipo."
                )
                
                return redirect('plans:subscription_dashboard')
                
        except Exception as e:
            messages.error(request, f"Error al crear la solicitud: {str(e)}")
            return redirect('plans:request_upgrade')


# Las vistas de gestión de superuser han sido eliminadas - toda la gestión se hace desde el admin de Django