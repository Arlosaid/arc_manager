# apps/plans/views.py (actualizado)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import PermissionDenied
import logging

from .models import Plan, Subscription, UpgradeRequest
from apps.orgs.models import Organization


# El logger se configurará localmente en cada función para evitar problemas de inicialización


# Mixins para verificación de permisos
class OrgAdminRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de org_admin"""
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and hasattr(user, 'is_org_admin') and user.is_org_admin
    
    def handle_no_permission(self):
        raise PermissionDenied("Necesitas permisos de administrador de organización.")


# Vistas para usuarios autenticados
class SubscriptionDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard de suscripción simplificado.
    La vista solo obtiene los objetos principales, y la lógica de presentación
    se delega completamente a la plantilla.
    """
    template_name = 'plans/subscription_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        organization = getattr(user, 'organization', None)
        
        if not organization:
            context['no_organization'] = True
            return context
        
        # Usar el servicio simplificado para obtener o crear la suscripción
        subscription = Subscription.objects.filter(organization=organization).first()
        if not subscription:
            trial_plan = Plan.get_trial_plan()
            if trial_plan:
                 subscription = Subscription.objects.create(
                    organization=organization,
                    plan=trial_plan
                )
            else:
                # Fallback por si no hay plan de prueba
                context['error'] = "No se pudo inicializar la suscripción. No hay un plan de prueba configurado."
                return context

        # Actualiza el estado al cargar la página
        subscription.update_status()

        context['subscription'] = subscription
        context['organization'] = organization
        context['is_org_admin'] = user.is_org_admin
        
        # Pasar las solicitudes de upgrade directamente a la plantilla
        context['pending_request'] = UpgradeRequest.objects.filter(
            organization=organization,
            status='pending'
        ).first()
        
        # Pasar los planes disponibles para que la plantilla decida si mostrarlos
        context['available_plans'] = Plan.objects.filter(
            is_active=True,
            price__gt=subscription.plan.price
        ).order_by('price')

        # Pasar el historial de pagos directamente
        context['payment_history'] = subscription.get_payment_history(limit=5)
        
        return context


# Las Vistas de Superusuario y API innecesarias han sido eliminadas para el MVP.


class RequestUpgradeView(LoginRequiredMixin, OrgAdminRequiredMixin, TemplateView):
    """Vista simplificada para que los usuarios soliciten un upgrade de plan."""
    template_name = 'plans/request_upgrade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.user.organization
        subscription = get_object_or_404(Subscription, organization=organization)

        context['subscription'] = subscription
        context['has_pending_request'] = UpgradeRequest.objects.filter(
            organization=organization,
            status='pending'
        ).exists()
        
        if not context['has_pending_request']:
            context['available_plans'] = Plan.objects.filter(
                is_active=True,
                price__gt=subscription.plan.price
            ).order_by('price')
            
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesa una solicitud de upgrade de forma simple y directa."""
        organization = request.user.organization
        subscription = get_object_or_404(Subscription, organization=organization)
        requested_plan_id = request.POST.get('requested_plan')
        
        # 1. Verificar que no haya una solicitud pendiente
        if UpgradeRequest.objects.filter(organization=organization, status='pending').exists():
            messages.warning(request, "Ya tienes una solicitud de upgrade pendiente.")
            return redirect('plans:subscription_dashboard')

        # 2. Validar el plan solicitado
        if not requested_plan_id:
            messages.error(request, "Debes seleccionar un plan.")
            return redirect('plans:request_upgrade')
            
        try:
            requested_plan = Plan.objects.get(id=requested_plan_id, is_active=True)
        except Plan.DoesNotExist:
            messages.error(request, "El plan seleccionado no es válido.")
            return redirect('plans:request_upgrade')
            
        # 3. Validar que sea un upgrade
        if requested_plan.price <= subscription.plan.price:
            messages.error(request, "Solo puedes hacer un upgrade a un plan de mayor valor.")
            return redirect('plans:request_upgrade')

        # 4. Crear la solicitud
        try:
            with transaction.atomic():
                UpgradeRequest.objects.create(
                    organization=organization,
                    current_plan=subscription.plan,
                    requested_plan=requested_plan,
                    amount=requested_plan.price
                )
                
            messages.success(
                request, 
                f"Tu solicitud de upgrade a {requested_plan.display_name} ha sido enviada. "
                "Recibirás instrucciones de pago una vez que sea aprobada."
            )
            return redirect('plans:subscription_dashboard')
                
        except Exception as e:
            logging.getLogger(__name__).error(f"Error al crear solicitud de upgrade: {e}", exc_info=True)
            messages.error(request, "Ocurrió un error al procesar tu solicitud. Por favor, contacta a soporte.")
            return redirect('plans:request_upgrade')