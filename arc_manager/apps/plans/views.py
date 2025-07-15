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
from django.utils.dateparse import parse_datetime
import logging

from .models import Plan, Subscription, UpgradeRequest
from .services import SubscriptionService
from apps.orgs.models import Organization

# El logger se configurará localmente en cada función para evitar problemas de inicialización


# Mixins para verificación de permisos
class OrgAdminRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de org_admin"""
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_org_admin
    
    def handle_no_permission(self):
        # NO mostrar mensaje aquí - usar PermissionDenied que es más estándar
        # y evita mensajes duplicados si hay redirecciones
        raise PermissionDenied("Necesitas permisos de administrador de organización.")


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
        
        # NO mostrar mensaje automático aquí - es confuso y innecesario
        # Si se necesita comunicar algo sobre el trial, mejor hacerlo en el template
        
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
        
        # Verificar solicitudes de upgrade pendientes
        pending_request = UpgradeRequest.objects.filter(
            organization=organization,
            status__in=['pending', 'approved']
        ).first()
        
        context['has_pending_request'] = bool(pending_request)
        context['pending_request'] = pending_request
        
        # Planes disponibles para upgrade (solo para admins de org y sin solicitudes pendientes)
        if context['is_org_admin'] and not pending_request:
            context['available_plans'] = Plan.objects.filter(
                is_active=True,
                price__gt=subscription.plan.price
            ).order_by('price')
        
        # Historial de pagos simplificado (últimos 5)
        payment_history = []
        if subscription.metadata and subscription.metadata.get('payment_history'):
            raw_history = subscription.metadata['payment_history'][-5:]
            for payment in raw_history:
                # Convertir fecha ISO string a datetime object
                if isinstance(payment.get('date'), str):
                    try:
                        payment['date'] = parse_datetime(payment['date'])
                    except (ValueError, TypeError):
                        # Si falla, usar fecha actual
                        payment['date'] = timezone.now()
                elif not payment.get('date'):
                    payment['date'] = timezone.now()
                
                payment_history.append(payment)
            
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
        logger = logging.getLogger(__name__)
        
        user = self.request.user
        organization = user.organization
        
        logger.info(f"GET RequestUpgradeView - Usuario: {user.email}, Organización: {organization.name if organization else 'None'}")
        
        if not organization:
            logger.warning(f"Usuario {user.email} no tiene organización asignada")
            context['no_organization'] = True
            return context
        
        # Obtener suscripción actual
        subscription = get_object_or_404(Subscription, organization=organization)
        logger.info(f"Suscripción actual: {subscription.plan.display_name} - Estado: {subscription.status}")
        
        # Verificar solicitud pendiente
        pending_request = UpgradeRequest.objects.filter(
            organization=organization,
            status__in=['pending', 'approved']
        ).first()
        
        if pending_request:
            logger.info(f"Solicitud pendiente encontrada: ID {pending_request.id} - Estado: {pending_request.status}")
        else:
            logger.info("No se encontraron solicitudes pendientes")
        
        context.update({
            'subscription': subscription,
            'current_plan': subscription.plan,
            'organization': organization,
            'has_pending_request': bool(pending_request),
            'pending_request': pending_request,
        })
        
        if not pending_request:
            # Planes disponibles para upgrade
            available_plans = Plan.objects.filter(
                is_active=True,
                price__gt=subscription.plan.price
            ).order_by('price')
            
            logger.info(f"Planes disponibles para upgrade: {list(available_plans.values_list('display_name', flat=True))}")
            context['available_plans'] = available_plans
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar solicitud de upgrade"""
        logger = logging.getLogger(__name__)
        logger.info(f"POST RequestUpgradeView iniciado - Usuario: {request.user.email}")
        logger.info(f"POST data: {dict(request.POST)}")
        
        user = request.user
        organization = user.organization
        
        if not organization:
            logger.error(f"Usuario {user.email} no tiene organización asignada en POST")
            messages.error(request, "No tienes una organización asignada.")
            return redirect('plans:subscription_dashboard')
        
        logger.info(f"Organización: {organization.name}")
        
        subscription = get_object_or_404(Subscription, organization=organization)
        logger.info(f"Suscripción: {subscription.plan.display_name}")
        
        # Verificar solicitud pendiente o aprobada (no se pueden hacer múltiples)
        existing_request = UpgradeRequest.objects.filter(
            organization=organization,
            status__in=['pending', 'approved']
        ).first()
        
        if existing_request:
            logger.warning(f"Solicitud existente encontrada: ID {existing_request.id} - Estado: {existing_request.status}")
            if existing_request.status == 'pending':
                messages.warning(
                    request, 
                    "Ya tienes una solicitud de upgrade pendiente. Por favor espera a que sea procesada."
                )
            elif existing_request.status == 'approved':
                messages.info(
                    request, 
                    "Tu solicitud de upgrade ya fue aprobada. Tu nuevo plan está activo."
                )
            return redirect('plans:request_upgrade')
        
        # Validar ventana de tiempo - prevenir spam (no más de 1 solicitud por minuto)
        recent_request = UpgradeRequest.objects.filter(
            organization=organization,
            requested_date__gte=timezone.now() - timedelta(minutes=1)
        ).first()
        
        if recent_request:
            logger.warning(f"Solicitud reciente encontrada: ID {recent_request.id} - Fecha: {recent_request.requested_date}")
            messages.warning(
                request, 
                "Has enviado una solicitud muy recientemente. Por favor espera un momento antes de intentar nuevamente."
            )
            return redirect('plans:request_upgrade')
        
        # Validar plan solicitado
        requested_plan_id = request.POST.get('requested_plan')
        logger.info(f"Plan solicitado ID: {requested_plan_id}")
        
        if not requested_plan_id:
            logger.error("No se proporcionó requested_plan en POST")
            messages.error(request, "Debes seleccionar un plan.")
            return redirect('plans:request_upgrade')
        
        try:
            requested_plan = get_object_or_404(Plan, id=requested_plan_id, is_active=True)
            logger.info(f"Plan solicitado: {requested_plan.display_name} - Precio: {requested_plan.price}")
        except Exception as e:
            logger.error(f"Error al obtener plan solicitado: {str(e)}")
            messages.error(request, "Plan no válido.")
            return redirect('plans:request_upgrade')
        
        if requested_plan.price <= subscription.plan.price:
            logger.error(f"Intento de downgrade - Plan actual: {subscription.plan.price}, Solicitado: {requested_plan.price}")
            messages.error(request, "Solo puedes hacer upgrade a un plan superior.")
            return redirect('plans:request_upgrade')
        
        # Crear solicitud de upgrade
        try:
            with transaction.atomic():
                logger.info("Iniciando creación de solicitud de upgrade")
                
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
                
                logger.info(f"Solicitud de upgrade creada exitosamente: ID {upgrade_request.id}")
                
                # Enviar instrucciones de pago
                try:
                    logger.info("Enviando instrucciones de pago")
                    email_sent = upgrade_request._send_payment_instructions()
                    logger.info(f"Email enviado: {email_sent}")
                except Exception as e:
                    logger.error(f"Error al enviar instrucciones de pago: {str(e)}", exc_info=True)
                
                messages.success(
                    request, 
                    f"Tu solicitud de upgrade a {requested_plan.display_name} ha sido enviada. "
                    "Revisa tu email para encontrar las instrucciones de pago."
                )
                
                logger.info("Solicitud de upgrade procesada exitosamente")
                return redirect('plans:subscription_dashboard')
                
        except Exception as e:
            logger.error(f"Error al crear solicitud de upgrade para organización {organization.id}: {str(e)}", exc_info=True)
            messages.error(request, "Ha ocurrido un error al procesar tu solicitud. Por favor, contacta con soporte técnico.")
            return redirect('plans:request_upgrade')