import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


logger = logging.getLogger('arc_manager.multitenant')


class TenantValidationMiddleware(MiddlewareMixin):
    """Middleware para validar límites de tenant en tiempo real"""
    
    # URLs que no requieren validación de tenant
    EXCLUDED_PATHS = [
        '/admin/',
        '/accounts/login/',
        '/accounts/logout/',
        '/api/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        # Saltar validación para paths excluidos
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return None
        
        # Solo validar usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Los superusers no tienen restricciones
        if request.user.is_superuser:
            return None
        
        # Validar organización del usuario
        if not request.user.organization:
            logger.warning(f"Usuario {request.user.email} sin organización intentó acceder a {request.path}")
            
            # Para requests AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes una organización asignada',
                    'redirect': reverse('main:home')
                }, status=403)
            
            # Para requests normales, redirigir SIN mensaje (evitar spam)
            # El mensaje se mostrará solo en páginas específicas
            return redirect('main:home')
        
        # Validar estado de la suscripción
        subscription_status = self.validate_subscription(request.user.organization)
        
        if not subscription_status['is_valid']:
            logger.warning(
                f"Organización {request.user.organization.name} con suscripción inválida: {subscription_status['reason']}"
            )
            
            # Para requests AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': subscription_status['message'],
                    'subscription_required': True
                }, status=403)
            
            # Solo mostrar mensaje en paths específicos para evitar spam
            # Y solo una vez por sesión
            if (self.should_show_subscription_warning(request.path) and 
                not request.session.get(f'subscription_warning_{subscription_status["reason"]}_shown', False)):
                
                messages.warning(request, subscription_status['message'])
                request.session[f'subscription_warning_{subscription_status["reason"]}_shown'] = True
        
        return None
    
    def validate_subscription(self, organization):
        """Validar estado de suscripción de la organización"""
        try:
            subscription = organization.get_subscription()
            
            if not subscription:
                return {
                    'is_valid': False,
                    'reason': 'no_subscription',
                    'message': 'Tu organización no tiene una suscripción activa. Contacta con soporte.'
                }
            
            if not subscription.is_active:
                days_remaining = subscription.days_remaining
                
                if days_remaining <= 0:
                    return {
                        'is_valid': False,
                        'reason': 'expired',
                        'message': 'Tu suscripción ha expirado. Contacta con soporte para renovar.'
                    }
                elif days_remaining <= 3:
                    return {
                        'is_valid': True,  # Aún válida pero con advertencia
                        'reason': 'expires_soon',
                        'message': f'Tu suscripción expira en {days_remaining} días. Renueva pronto para evitar interrupciones.'
                    }
            
            # Validar límites de usuarios
            current_users = organization.users.filter(is_active=True).count()
            max_users = subscription.plan.max_users
            
            if current_users > max_users:
                return {
                    'is_valid': True,  # No bloquear, solo advertir
                    'reason': 'user_limit_exceeded',
                    'message': f'Tu organización ha excedido el límite de usuarios ({current_users}/{max_users}). Considera actualizar tu plan.'
                }
            
            return {
                'is_valid': True,
                'reason': 'valid',
                'message': None
            }
            
        except Exception as e:
            logger.error(f"Error validando suscripción para {organization.name}: {str(e)}")
            return {
                'is_valid': True,  # En caso de error, no bloquear
                'reason': 'validation_error',
                'message': None
            }
    
    def should_show_subscription_warning(self, path):
        """Determinar si se debe mostrar advertencia de suscripción en esta ruta"""
        warning_paths = [
            '/dashboard/',
            '/users/',
            '/plans/',
        ]
        return any(path.startswith(warn_path) for warn_path in warning_paths)


class OrganizationContextMiddleware(MiddlewareMixin):
    """Middleware para agregar contexto de organización a todas las requests"""
    
    def process_request(self, request):
        # Agregar información de organización al request
        if request.user.is_authenticated and request.user.organization:
            organization = request.user.organization
            
            request.organization = organization
            request.subscription = organization.get_subscription()
            request.organization_limits = organization.get_subscription_limits()
            
            # Información útil para templates
            request.can_add_user = organization.can_add_user()
            request.is_org_admin = request.user.is_org_admin
            request.org_user_count = organization.users.filter(is_active=True).count()
            request.org_max_users = organization.get_max_users()
        else:
            request.organization = None
            request.subscription = None
            request.organization_limits = None
            request.can_add_user = False
            request.is_org_admin = False
            request.org_user_count = 0
            request.org_max_users = 0
        
        return None 