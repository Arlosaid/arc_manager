from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from django.conf import settings
import logging

from .services import SubscriptionService

logger = logging.getLogger(__name__)

class SubscriptionAccessMiddleware(MiddlewareMixin):
    """
    Middleware para verificar automáticamente el acceso según el estado de suscripción
    
    MVP: Bloquea acceso a módulos no permitidos según el estado de suscripción
    Configurable por settings y rutas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rutas que siempre están permitidas (sin verificación de suscripción)
        self.always_allowed_paths = [
            '/admin/',
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/password_reset/',
            '/plans/',
            '/api/check-limits/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # Rutas que requieren acceso completo
        self.full_access_required_paths = [
            '/dashboard/',
            '/orgs/',
            '/users/',
            '/projects/',  # Para el futuro
            '/reports/',   # Para el futuro
        ]
        
        # Rutas que pueden funcionar con acceso limitado
        self.limited_access_paths = [
            '/plans/',
            '/subscription/',
            '/billing/',
        ]
        
        # Configuración desde settings
        self.enabled = getattr(settings, 'SUBSCRIPTION_ACCESS_MIDDLEWARE_ENABLED', True)
        self.redirect_url = getattr(settings, 'SUBSCRIPTION_EXPIRED_REDIRECT_URL', 'plans:subscription_dashboard')
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Procesa cada request para verificar permisos de suscripción
        """
        # Verificar si el middleware está habilitado
        if not self.enabled:
            return None
        
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return None
        
        # Verificar si es superuser (siempre permitido)
        if request.user.is_superuser:
            return None
        
        # Verificar si la ruta está en las permitidas siempre
        if self._is_always_allowed(request.path):
            return None
        
        # Verificar si el usuario tiene organización
        if not hasattr(request.user, 'organization') or not request.user.organization:
            # Usuario sin organización - redirigir a configuración
            if not request.path.startswith('/accounts/'):
                messages.warning(request, 'Necesitas estar asociado a una organización para acceder a esta sección.')
                return redirect('orgs:my_organization')
            return None
        
        # Obtener suscripción
        subscription = SubscriptionService.get_subscription_or_create(request.user.organization)
        if not subscription:
            # Error obteniendo suscripción
            messages.error(request, 'Error verificando tu suscripción. Por favor contacta al soporte.')
            return redirect(self.redirect_url)
        
        # Determinar el módulo actual
        current_module = self._get_current_module(request.path)
        
        # Verificar permisos de acceso
        access_result = SubscriptionService.check_access_permissions(subscription, current_module)
        
        if not access_result.get('has_access', False):
            return self._handle_access_denied(request, access_result)
        
        # Agregar información de suscripción al request para uso posterior
        request.subscription = subscription
        request.subscription_access = access_result
        
        return None
    
    def _is_always_allowed(self, path):
        """Verifica si la ruta está siempre permitida"""
        for allowed_path in self.always_allowed_paths:
            if path.startswith(allowed_path):
                return True
        return False
    
    def _get_current_module(self, path):
        """Determina el módulo actual basado en la ruta"""
        if path.startswith('/dashboard/'):
            return 'dashboard'
        elif path.startswith('/orgs/'):
            return 'organizations'
        elif path.startswith('/users/'):
            return 'users'
        elif path.startswith('/projects/'):
            return 'projects'
        elif path.startswith('/reports/'):
            return 'reports'
        elif path.startswith('/plans/') or path.startswith('/subscription/'):
            return 'plans'
        elif path.startswith('/billing/'):
            return 'billing'
        else:
            return 'general'
    
    def _handle_access_denied(self, request, access_result):
        """Maneja el acceso denegado según el tipo de request"""
        
        # Verificar si es un request AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': access_result.get('message', 'Acceso denegado'),
                'access_level': access_result.get('access_level', 'none'),
                'redirect_url': reverse(self.redirect_url) if access_result.get('redirect_to') else None
            }, status=403)
        
        # Request normal - redirigir con mensaje
        message = access_result.get('message', 'Acceso denegado')
        
        if access_result.get('access_level') == 'limited':
            messages.warning(request, message)
        else:
            messages.error(request, message)
        
        # Redirigir a la URL apropiada
        redirect_to = access_result.get('redirect_to', self.redirect_url)
        return redirect(redirect_to)


class SubscriptionInfoMiddleware(MiddlewareMixin):
    """
    Middleware ligero para agregar información de suscripción al contexto
    Útil para mostrar alertas o información en el template
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Agrega información de suscripción al request"""
        
        # Solo para usuarios autenticados con organización
        if (request.user.is_authenticated and 
            hasattr(request.user, 'organization') and 
            request.user.organization):
            
            subscription = SubscriptionService.get_subscription_or_create(request.user.organization)
            if subscription:
                # Agregar información útil al request
                request.subscription_info = {
                    'status': subscription.subscription_status,
                    'display_status': subscription.get_subscription_status_display(),
                    'is_active': subscription.is_active,
                    'is_expired': subscription.is_expired,
                    'is_in_grace': subscription.is_in_grace_period,
                    'days_remaining': subscription.days_remaining,
                    'plan_name': subscription.plan.display_name,
                    'expires_soon': subscription.days_remaining <= 7 and subscription.days_remaining > 0,
                    'needs_attention': subscription.is_expired or subscription.is_in_grace_period,
                }
        
        return None


def subscription_required(allowed_statuses=None, redirect_url=None):
    """
    Decorador para vistas que requieren suscripción específica
    
    Uso:
    @subscription_required(allowed_statuses=['trial_active', 'basic_active'])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not hasattr(request.user, 'organization') or not request.user.organization:
                messages.warning(request, 'Necesitas estar asociado a una organización.')
                return redirect('orgs:my_organization')
            
            subscription = SubscriptionService.get_subscription_or_create(request.user.organization)
            if not subscription:
                messages.error(request, 'Error verificando tu suscripción.')
                return redirect(redirect_url or 'plans:subscription_dashboard')
            
            # Verificar estado específico si se requiere
            if allowed_statuses and subscription.subscription_status not in allowed_statuses:
                messages.error(request, 'Tu suscripción no permite acceder a esta función.')
                return redirect(redirect_url or 'plans:subscription_dashboard')
            
            # Verificar acceso general
            access_result = SubscriptionService.check_access_permissions(subscription)
            if not access_result.get('has_access', False):
                message = access_result.get('message', 'Acceso denegado')
                messages.error(request, message)
                return redirect(redirect_url or 'plans:subscription_dashboard')
            
            # Agregar subscription al request para uso en la vista
            request.subscription = subscription
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def full_access_required(view_func):
    """
    Decorador para vistas que requieren acceso completo (no expirado)
    
    Uso:
    @full_access_required
    def my_view(request):
        ...
    """
    return subscription_required(allowed_statuses=['trial_active', 'basic_active', 'basic_grace'])(view_func)


def trial_or_paid_required(view_func):
    """
    Decorador para vistas que requieren trial activo o plan de pago
    
    Uso:
    @trial_or_paid_required
    def my_view(request):
        ...
    """
    return subscription_required(allowed_statuses=['trial_active', 'basic_active'])(view_func)


def basic_plan_required(view_func):
    """
    Decorador para vistas que requieren plan básico específicamente
    
    Uso:
    @basic_plan_required
    def my_view(request):
        ...
    """
    return subscription_required(allowed_statuses=['basic_active', 'basic_grace'])(view_func)


# Utilidades para templates
def get_subscription_context(request):
    """
    Función auxiliar para obtener contexto de suscripción en templates
    """
    if not hasattr(request, 'subscription'):
        return {}
    
    subscription = request.subscription
    
    return {
        'subscription': subscription,
        'subscription_summary': subscription.get_subscription_summary(),
        'subscription_alerts': SubscriptionService._get_subscription_alerts(subscription),
        'subscription_actions': SubscriptionService._get_available_actions(subscription),
        'usage_stats': SubscriptionService._get_usage_stats(subscription),
    } 