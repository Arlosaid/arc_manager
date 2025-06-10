from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def check_user_limit(view_func):
    """Decorador para verificar límite de usuarios antes de crear"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST' and request.user.organization:
            org = request.user.organization
            if not org.can_add_user():
                limit_info = org.can_add_user_detailed()
                
                error_message = (
                    f"No se puede crear el usuario. Tu organización ha alcanzado "
                    f"el límite de {org.get_max_users()} usuarios. "
                    f"Actualmente tienes {limit_info['total_users']} usuarios "
                    f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos)."
                )
                
                if limit_info['has_inactive_users']:
                    error_message += " Considera reactivar usuarios inactivos o contacta con soporte."
                else:
                    error_message += " Contacta con soporte para incrementar tu límite."
                
                # Para requests AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_message,
                        'limit_info': limit_info
                    }, status=400)
                
                # Para requests normales
                messages.error(request, error_message)
                return redirect('users:user_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_org_admin(view_func):
    """Decorador que requiere permisos de administrador de organización"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Debes estar autenticado.")
        
        if not request.user.is_org_admin and not request.user.is_superuser:
            # Para requests AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Necesitas permisos de administrador de organización.',
                    'permission_denied': True
                }, status=403)
            
            messages.error(request, "Necesitas permisos de administrador de organización.")
            return redirect('main:home')
        
        if not request.user.organization and not request.user.is_superuser:
            messages.error(request, "No tienes una organización asignada.")
            return redirect('main:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_active_subscription(view_func):
    """Decorador que requiere suscripción activa"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if not request.user.organization:
            messages.error(request, "No tienes una organización asignada.")
            return redirect('main:home')
        
        subscription = request.user.organization.get_subscription()
        if not subscription or not subscription.is_active:
            error_message = "Tu suscripción no está activa. Contacta con soporte."
            
            # Para requests AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message,
                    'subscription_required': True
                }, status=403)
            
            messages.error(request, error_message)
            return redirect('plans:subscription_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_plan_feature(feature_name):
    """Decorador que requiere una característica específica del plan"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.organization:
                messages.error(request, "No tienes una organización asignada.")
                return redirect('main:home')
            
            subscription = request.user.organization.get_subscription()
            if not subscription:
                messages.error(request, "No tienes una suscripción activa.")
                return redirect('plans:subscription_dashboard')
            
            # Verificar si el plan incluye la característica
            plan_features = subscription.plan.get_feature_list()
            if feature_name not in plan_features:
                error_message = f"Esta característica ({feature_name}) no está disponible en tu plan actual."
                
                # Para requests AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_message,
                        'upgrade_required': True,
                        'current_plan': subscription.plan.display_name
                    }, status=403)
                
                messages.error(request, error_message + " Considera actualizar tu plan.")
                return redirect('plans:subscription_dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_organization_context(view_func):
    """Decorador para validar que el usuario esté operando en su organización"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Los superusers pueden operar en cualquier organización
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Obtener ID de organización desde la URL si está presente
        org_id = kwargs.get('org_id') or request.GET.get('org_id') or request.POST.get('org_id')
        
        if org_id:
            # Verificar que el usuario pertenece a esta organización
            if request.user.organization and str(request.user.organization.id) != str(org_id):
                error_message = "No puedes realizar acciones en otra organización."
                
                # Para requests AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_message,
                        'organization_mismatch': True
                    }, status=403)
                
                messages.error(request, error_message)
                return redirect('main:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper 