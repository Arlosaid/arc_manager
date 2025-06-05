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
class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere permisos de superusuario"""
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para acceder a esta sección.")
        return redirect('main:home')


class OrgAdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere ser admin de organización"""
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_org_admin or user.is_superuser)
    
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


class UpgradePlanView(LoginRequiredMixin, TemplateView):
    """Vista para actualizar plan (MVP con proceso manual)"""
    template_name = 'plans/upgrade_plan.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        organization = getattr(user, 'organization', None)
        
        if not organization or not hasattr(organization, 'subscription'):
            context['error'] = "No tienes una organización o suscripción válida"
            return context
        
        subscription = organization.subscription
        
        # Verificar que puede hacer upgrade
        if not user.is_org_admin and not user.is_superuser:
            context['error'] = "No tienes permisos para cambiar el plan"
            return context
        
        context['current_subscription'] = subscription
        context['organization'] = organization
        
        # Planes disponibles para upgrade
        available_plans = Plan.objects.filter(
            is_active=True,
            price__gt=subscription.plan.price
        ).order_by('price')
        
        context['available_plans'] = available_plans
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar solicitud de upgrade"""
        try:
            user = request.user
            organization = getattr(user, 'organization', None)
            
            # Logging para debug
            print(f"POST request recibido para upgrade de plan")
            print(f"Usuario: {user.email}")
            print(f"Organización: {organization.name if organization else 'None'}")
            print(f"POST data: {request.POST}")
            
            if not organization or not hasattr(organization, 'subscription'):
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes una organización válida'
                })
            
            # Verificar permisos
            if not user.is_org_admin and not user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permisos para cambiar el plan'
                })
            
            plan_id = request.POST.get('plan_id')
            if not plan_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID de plan no proporcionado'
                })
            
            try:
                new_plan = get_object_or_404(Plan, id=plan_id, is_active=True)
                subscription = organization.subscription
                
                # Verificar que es un upgrade
                if new_plan.price <= subscription.plan.price:
                    return JsonResponse({
                        'success': False,
                        'error': 'Solo puedes hacer upgrade a un plan superior'
                    })
                
                # Verificar si ya hay una solicitud pendiente
                existing_request = UpgradeRequest.objects.filter(
                    organization=organization,
                    status__in=['pending', 'approved', 'payment_pending']
                ).first()
                
                if existing_request:
                    return JsonResponse({
                        'success': False,
                        'error': f'Ya tienes una solicitud de upgrade {existing_request.get_status_display().lower()}. '
                                f'Contacta al administrador para más información.'
                    })
                
                # Crear solicitud de upgrade (NO cambiar el plan todavía)
                upgrade_request = UpgradeRequest.objects.create(
                    organization=organization,
                    current_plan=subscription.plan,
                    requested_plan=new_plan,
                    requested_by=user,
                    amount_due=new_plan.price,
                    request_notes=request.POST.get('notes', ''),
                    payment_method=request.POST.get('payment_method', 'transferencia')
                )
                
                print(f"Solicitud de upgrade creada: {upgrade_request.id}")
                
                # Enviar notificación al administrador
                self._send_admin_notification(upgrade_request)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Solicitud de upgrade a {new_plan.display_name} enviada correctamente. '
                             f'Te contactaremos pronto para aprobar y procesar tu solicitud.',
                    'request_id': upgrade_request.id,
                    'status': 'pending_approval'
                })
                
            except Plan.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Plan no encontrado o inactivo'
                })
            except Exception as e:
                print(f"Error interno en upgrade: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error procesando upgrade: {str(e)}'
                })
                
        except Exception as e:
            print(f"Error general en UpgradePlanView POST: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error del servidor: {str(e)}'
            })
    
    def _send_admin_notification(self, upgrade_request):
        """Envía notificación al administrador sobre nueva solicitud"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"🔔 Nueva Solicitud de Upgrade - {upgrade_request.organization.name}"
            message = f"""
Nueva solicitud de upgrade pendiente de aprobación:

DETALLES:
━━━━━━━━━━━━━━━━━━━━━━━━
• Organización: {upgrade_request.organization.name}
• Plan actual: {upgrade_request.current_plan.display_name} (${upgrade_request.current_plan.price}/mes)
• Plan solicitado: {upgrade_request.requested_plan.display_name} (${upgrade_request.requested_plan.price}/mes)
• Diferencia de precio: +${upgrade_request.price_difference}/mes
• Solicitado por: {upgrade_request.requested_by.get_full_name()} ({upgrade_request.requested_by.email})
• Fecha: {upgrade_request.requested_date.strftime('%d/%m/%Y %H:%M')}

ACCIONES REQUERIDAS:
━━━━━━━━━━━━━━━━━━━━━━━━
1. Revisar la solicitud en el panel de administración
2. Aprobar o rechazar la solicitud
3. Si se aprueba, el usuario recibirá instrucciones de pago

Panel de administración:
{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/plans/upgraderequest/{upgrade_request.id}/change/

Solicitudes pendientes:
{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/plans/upgraderequest/?status=pending
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@tudominio.com')
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
                recipient_list=[admin_email],
                fail_silently=True
            )
            
        except Exception as e:
            print(f"Error enviando notificación al admin: {e}")
    
    def _send_upgrade_confirmation_email(self, organization, old_plan, new_plan):
        """Envía email de confirmación de upgrade (DEPRECATED - usar UpgradeRequest)"""
        # Esta función ahora está deprecated, se usa el nuevo sistema
        pass


# Vistas de superusuario
class SuperuserPlanListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    """Lista de planes para superusuarios"""
    model = Plan
    template_name = 'plans/superuser/plan_list.html'
    context_object_name = 'plans'
    ordering = ['sort_order', 'price']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        plans = Plan.objects.all()
        context['total_plans'] = plans.count()
        context['active_plans'] = plans.filter(is_active=True).count()
        context['inactive_plans'] = plans.filter(is_active=False).count()
        
        # Planes destacados
        context['featured_plans'] = plans.filter(is_featured=True, is_active=True).count()
        
        return context


class SuperuserPlanCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    """Crear nuevo plan"""
    model = Plan
    form_class = PlanForm
    template_name = 'plans/superuser/plan_form.html'
    success_url = reverse_lazy('plans:superuser_list')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f"Plan '{form.instance.display_name}' creado exitosamente."
        )
        return super().form_valid(form)


class SuperuserPlanUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    """Editar plan existente"""
    model = Plan
    form_class = PlanForm
    template_name = 'plans/superuser/plan_form.html'
    success_url = reverse_lazy('plans:superuser_list')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f"Plan '{form.instance.display_name}' actualizado exitosamente."
        )
        return super().form_valid(form)


class SuperuserPlanDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    """Eliminar plan"""
    model = Plan
    template_name = 'plans/superuser/plan_confirm_delete.html'
    success_url = reverse_lazy('plans:superuser_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verificar si el plan tiene organizaciones asociadas
        context['has_organizations'] = self.object.subscription_set.exists()
        return context
    
    def delete(self, request, *args, **kwargs):
        plan = self.get_object()
        
        # Verificar que no tenga organizaciones activas
        if plan.subscription_set.exists():
            messages.error(
                request,
                f"No se puede eliminar el plan '{plan.display_name}' porque está siendo usado por organizaciones."
            )
            return redirect(self.success_url)
        
        messages.success(
            request,
            f"Plan '{plan.display_name}' eliminado exitosamente."
        )
        return super().delete(request, *args, **kwargs)


# Vistas para administradores de organización
class OrgPlanManagementView(LoginRequiredMixin, OrgAdminRequiredMixin, TemplateView):
    """Gestión de planes para administradores de organización - MVP Manual"""
    template_name = 'plans/org_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        organization = getattr(user, 'organization', None)
        
        if not organization:
            context['error'] = "No tienes una organización asignada"
            return context
        
        # Información de la organización y suscripción actual
        context['organization'] = organization
        subscription = getattr(organization, 'subscription', None)
        
        if subscription:
            context['current_subscription'] = subscription
            context['current_plan'] = subscription.plan
            
            # Estadísticas de uso
            context['usage_stats'] = {
                'users': {
                    'current': organization.get_user_count(),
                    'limit': subscription.plan.max_users,
                    'percentage': subscription.plan.get_usage_percentage(
                        organization.get_user_count(), 'users'
                    ),
                    'can_add': organization.can_add_user()
                },
                'storage': {
                    'current': 0,  # TODO: implementar cuando tengas storage
                    'limit': subscription.plan.storage_limit_gb,
                    'percentage': 0
                }
            }
            
            # Historial de pagos desde metadata
            payment_history = []
            if subscription.metadata and subscription.metadata.get('payment_history'):
                payment_history = subscription.metadata['payment_history'][-10:]  # Últimos 10
                payment_history.reverse()  # Más recientes primero
            context['payment_history'] = payment_history
            
            # Información de facturación
            context['billing_info'] = {
                'next_billing_date': subscription.next_billing_date,
                'days_remaining': subscription.days_remaining,
                'is_trial': subscription.is_trial,
                'trial_days_remaining': subscription.trial_days_remaining if subscription.is_trial else 0,
                'total_paid': sum([float(p.get('amount', 0)) for p in payment_history if p.get('status') == 'paid'])
            }
        else:
            context['no_subscription'] = True
        
        # Planes disponibles para upgrade/solicitud
        current_price = subscription.plan.price if subscription else 0
        context['available_plans'] = Plan.objects.filter(
            is_active=True,
            price__gt=current_price
        ).order_by('price')
        
        # Información de contacto para pagos manuales
        context['payment_methods'] = [
            {
                'name': 'Transferencia Bancaria',
                'description': 'Transferencia a cuenta bancaria',
                'details': 'Banco XYZ - Cuenta: 1234567890 - CLABE: 123456789012345678'
            },
            {
                'name': 'Depósito en Efectivo',
                'description': 'Depósito en sucursal bancaria',
                'details': 'Banco XYZ - Cuenta: 1234567890 - Referencia: Tu número de organización'
            }
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejo de solicitudes de cambio de plan"""
        action = request.POST.get('action')
        organization = getattr(request.user, 'organization', None)
        
        if not organization:
            messages.error(request, "No tienes una organización asignada")
            return redirect('plans:org_management')
        
        if action == 'request_upgrade':
            plan_id = request.POST.get('plan_id')
            payment_method = request.POST.get('payment_method')
            payment_reference = request.POST.get('payment_reference', '')
            notes = request.POST.get('notes', '')
            
            try:
                new_plan = Plan.objects.get(id=plan_id)
                subscription = organization.subscription
                
                # Crear solicitud en metadata de la suscripción
                if not subscription.metadata:
                    subscription.metadata = {}
                
                upgrade_requests = subscription.metadata.get('upgrade_requests', [])
                upgrade_requests.append({
                    'date': timezone.now().isoformat(),
                    'requested_plan': new_plan.name,
                    'requested_plan_name': new_plan.display_name,
                    'current_plan': subscription.plan.name,
                    'payment_method': payment_method,
                    'payment_reference': payment_reference,
                    'notes': notes,
                    'status': 'pending',
                    'requested_by': request.user.username,
                    'price_difference': float(new_plan.price - subscription.plan.price)
                })
                
                subscription.metadata['upgrade_requests'] = upgrade_requests
                subscription.save()
                
                # Enviar notificación por email (opcional)
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        subject=f'Solicitud de Upgrade - {organization.name}',
                        message=f'''
                        Nueva solicitud de upgrade de plan:
                        
                        Organización: {organization.name}
                        Plan actual: {subscription.plan.display_name}
                        Plan solicitado: {new_plan.display_name}
                        Método de pago: {payment_method}
                        Referencia: {payment_reference}
                        Notas: {notes}
                        
                        Por favor procesa esta solicitud en el panel de administración.
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@tudominio.com'],
                        fail_silently=True
                    )
                except:
                    pass  # No fallar si no se puede enviar email
                
                messages.success(
                    request,
                    f"Solicitud de upgrade a {new_plan.display_name} enviada correctamente. "
                    f"Te contactaremos pronto para confirmar el pago."
                )
                
            except Plan.DoesNotExist:
                messages.error(request, "Plan no encontrado")
            except Exception as e:
                messages.error(request, f"Error al procesar la solicitud: {str(e)}")
        
        elif action == 'report_payment':
            payment_amount = request.POST.get('payment_amount')
            payment_method = request.POST.get('payment_method')
            payment_reference = request.POST.get('payment_reference', '')
            payment_date = request.POST.get('payment_date')
            
            try:
                subscription = organization.subscription
                
                # Agregar reporte de pago a metadata
                if not subscription.metadata:
                    subscription.metadata = {}
                
                payment_reports = subscription.metadata.get('payment_reports', [])
                payment_reports.append({
                    'date_reported': timezone.now().isoformat(),
                    'payment_date': payment_date,
                    'amount': float(payment_amount),
                    'method': payment_method,
                    'reference': payment_reference,
                    'status': 'pending_verification',
                    'reported_by': request.user.username
                })
                
                subscription.metadata['payment_reports'] = payment_reports
                subscription.save()
                
                messages.success(
                    request,
                    "Pago reportado correctamente. Verificaremos la información y actualizaremos tu suscripción."
                )
                
            except Exception as e:
                messages.error(request, f"Error al reportar el pago: {str(e)}")
        
        return redirect('plans:org_management')


# Vista para procesar pagos manuales (solo para staff)
class ProcessPaymentView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para que el staff procese pagos manuales"""
    template_name = 'plans/process_payment.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Suscripciones con pagos pendientes
        pending_subscriptions = Subscription.objects.filter(
            payment_status='pending'
        ).select_related('organization', 'plan')
        
        context['pending_subscriptions'] = pending_subscriptions
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar pago manual"""
        subscription_id = request.POST.get('subscription_id')
        payment_reference = request.POST.get('payment_reference')
        amount = request.POST.get('amount')
        
        try:
            subscription = get_object_or_404(Subscription, id=subscription_id)
            amount = float(amount)
            
            # Procesar pago
            SubscriptionService.process_manual_payment(
                subscription.organization,
                amount,
                payment_reference
            )
            
            messages.success(
                request,
                f"Pago procesado para {subscription.organization.name}"
            )
            
        except Exception as e:
            messages.error(request, f"Error procesando pago: {str(e)}")
        
        return redirect('plans:process_payment')


# Funciones auxiliares y API
@login_required
def change_organization_plan(request):
    """Cambiar plan de organización (para admins de org)"""
    if request.method == 'POST':
        user = request.user
        organization = getattr(user, 'organization', None)
        
        if not organization or not (user.is_org_admin or user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para cambiar el plan'
            })
        
        plan_id = request.POST.get('plan_id')
        
        try:
            new_plan = get_object_or_404(Plan, id=plan_id, is_active=True)
            subscription = getattr(organization, 'subscription', None)
            
            if not subscription:
                # Crear nueva suscripción
                subscription = Subscription.objects.create(
                    organization=organization,
                    plan=new_plan
                )
            else:
                # Actualizar plan existente
                subscription.plan = new_plan
                subscription.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Plan cambiado a {new_plan.display_name}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


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
    
    if user.is_superuser:
        return redirect('plans:superuser_list')
    elif hasattr(user, 'organization') and user.organization and (user.is_org_admin or user.organization):
        return redirect('plans:subscription_dashboard')
    else:
        return redirect('plans:pricing')


# Nuevas vistas para gestión manual del MVP
class SuperuserSubscriptionManagementView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    """Vista especializada para gestión manual de suscripciones (MVP)"""
    template_name = 'plans/superuser/subscription_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        total_orgs = Organization.objects.count()
        total_subscriptions = Subscription.objects.count()
        active_subscriptions = Subscription.objects.filter(status='active').count()
        trial_subscriptions = Subscription.objects.filter(status='trial').count()
        expired_subscriptions = Subscription.objects.filter(status='expired').count()
        pending_payments = Subscription.objects.filter(payment_status='pending').count()
        
        context['stats'] = {
            'total_orgs': total_orgs,
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'trial_subscriptions': trial_subscriptions,
            'expired_subscriptions': expired_subscriptions,
            'pending_payments': pending_payments,
        }
        
        # Suscripciones que requieren atención (próximas a vencer o con pagos pendientes)
        from datetime import timedelta
        next_week = timezone.now() + timedelta(days=7)
        
        context['attention_required'] = Subscription.objects.filter(
            models.Q(end_date__lte=next_week, status__in=['active', 'trial']) |
            models.Q(payment_status='pending')
        ).select_related('organization', 'plan').order_by('end_date')[:10]
        
        # Organizaciones recientes sin suscripción o con suscripción trial
        context['recent_organizations'] = Organization.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('subscription', 'subscription__plan').order_by('-created_at')[:10]
        
        # Planes disponibles para asignación rápida
        context['available_plans'] = Plan.objects.filter(is_active=True).order_by('sort_order')
        
        # Ingresos mensuales estimados
        monthly_revenue = 0
        for plan in Plan.objects.filter(is_active=True):
            plan_subscriptions = Subscription.objects.filter(plan=plan, status='active').count()
            monthly_revenue += plan.price * plan_subscriptions
        
        context['monthly_revenue'] = monthly_revenue
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejo de acciones rápidas desde la vista"""
        action = request.POST.get('action')
        org_id = request.POST.get('organization_id')
        plan_id = request.POST.get('plan_id')
        
        try:
            organization = Organization.objects.get(id=org_id)
            
            if action == 'assign_plan':
                plan = Plan.objects.get(id=plan_id)
                
                # Obtener o crear suscripción
                subscription, created = Subscription.objects.get_or_create(
                    organization=organization,
                    defaults={'plan': plan}
                )
                
                if not created:
                    subscription.plan = plan
                
                # Configurar según el tipo de plan
                if plan.is_trial:
                    subscription.status = 'trial'
                    subscription.payment_status = 'pending'
                    subscription.end_date = timezone.now() + timedelta(days=plan.trial_days)
                else:
                    subscription.status = 'active'
                    subscription.payment_status = 'paid'
                    subscription.last_payment_date = timezone.now()
                    subscription.end_date = timezone.now() + timedelta(days=30)  # 1 mes por defecto
                
                subscription.save()
                
                messages.success(
                    request, 
                    f"Plan {plan.display_name} asignado correctamente a {organization.name}"
                )
                
            elif action == 'extend_subscription':
                days = int(request.POST.get('days', 30))
                subscription = organization.subscription
                subscription.extend_subscription(days)
                
                # Marcar como pagado si se extiende
                subscription.payment_status = 'paid'
                subscription.last_payment_date = timezone.now()
                subscription.save()
                
                messages.success(
                    request,
                    f"Suscripción de {organization.name} extendida por {days} días"
                )
                
            elif action == 'mark_payment':
                subscription = organization.subscription
                subscription.payment_status = 'paid'
                subscription.last_payment_date = timezone.now()
                
                # Agregar al historial
                if not subscription.metadata:
                    subscription.metadata = {}
                
                payment_history = subscription.metadata.get('payment_history', [])
                payment_history.append({
                    'date': timezone.now().isoformat(),
                    'amount': float(subscription.plan.price),
                    'method': 'manual',
                    'status': 'paid',
                    'note': f'Pago manual registrado por {request.user.username}',
                    'reference': request.POST.get('payment_reference', '')
                })
                subscription.metadata['payment_history'] = payment_history
                subscription.save()
                
                messages.success(
                    request,
                    f"Pago registrado para {organization.name}"
                )
                
        except Organization.DoesNotExist:
            messages.error(request, "Organización no encontrada")
        except Plan.DoesNotExist:
            messages.error(request, "Plan no encontrado")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('plans:superuser_subscription_management')


class ManualPaymentProcessView(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    """Vista para procesar pagos manuales"""
    template_name = 'plans/superuser/manual_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Suscripciones con pagos pendientes
        context['pending_payments'] = Subscription.objects.filter(
            payment_status='pending'
        ).select_related('organization', 'plan').order_by('end_date')
        
        # Suscripciones próximas a vencer
        next_week = timezone.now() + timedelta(days=7)
        context['expiring_soon'] = Subscription.objects.filter(
            end_date__lte=next_week,
            status__in=['active', 'trial']
        ).select_related('organization', 'plan').order_by('end_date')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar pago manual"""
        subscription_id = request.POST.get('subscription_id')
        payment_method = request.POST.get('payment_method', 'transferencia')
        payment_amount = request.POST.get('payment_amount')
        payment_reference = request.POST.get('payment_reference', '')
        extend_months = int(request.POST.get('extend_months', 1))
        
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            
            # Extender suscripción
            days_to_extend = extend_months * 30
            subscription.extend_subscription(days_to_extend)
            
            # Marcar como pagado
            subscription.payment_status = 'paid'
            subscription.last_payment_date = timezone.now()
            
            # Actualizar historial de pagos
            if not subscription.metadata:
                subscription.metadata = {}
            
            payment_history = subscription.metadata.get('payment_history', [])
            payment_history.append({
                'date': timezone.now().isoformat(),
                'amount': float(payment_amount) if payment_amount else float(subscription.plan.price * extend_months),
                'method': payment_method,
                'status': 'paid',
                'reference': payment_reference,
                'months_extended': extend_months,
                'processed_by': request.user.username,
                'note': f'Pago manual procesado - {payment_method}'
            })
            subscription.metadata['payment_history'] = payment_history
            subscription.save()
            
            messages.success(
                request,
                f"Pago procesado correctamente para {subscription.organization.name}. "
                f"Suscripción extendida por {extend_months} mes(es)."
            )
            
        except Subscription.DoesNotExist:
            messages.error(request, "Suscripción no encontrada")
        except Exception as e:
            messages.error(request, f"Error al procesar el pago: {str(e)}")
        
        return redirect('plans:manual_payment')