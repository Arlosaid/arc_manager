"""
Utilidades de cache específicas para organizaciones
Ejemplos prácticos de cómo usar Redis en el proyecto
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib

# Timeout por defecto para cache de organización
ORG_CACHE_TIMEOUT = 60 * 15  # 15 minutos

def cache_organization_data(timeout=ORG_CACHE_TIMEOUT):
    """
    Decorator para cachear datos de organización
    Útil para datos que no cambian frecuentemente
    """
    def decorator(func):
        @wraps(func)
        def wrapper(organization_id, *args, **kwargs):
            # Crear clave única para esta organización y función
            cache_key = f"org_data:{organization_id}:{func.__name__}"
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Si no está en cache, ejecutar función y guardar resultado
            result = func(organization_id, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def cache_user_permissions(timeout=60*30):  # 30 minutos
    """
    Cache para permisos de usuario por organización
    Evita consultas repetidas a la BD para verificar permisos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, organization_id, *args, **kwargs):
            cache_key = f"user_perms:{user_id}:{organization_id}:{func.__name__}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(user_id, organization_id, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

class OrganizationCacheMixin:
    """
    Mixin para vistas que manejan datos de organización
    Proporciona métodos fáciles para cache
    """
    
    def get_cached_organization_stats(self, organization_id):
        """
        Obtiene estadísticas de organización desde cache
        Ejemplo: número de usuarios, planes activos, etc.
        """
        cache_key = f"org_stats:{organization_id}"
        stats = cache.get(cache_key)
        
        if stats is None:
            # Calcular estadísticas (esto sería costoso sin cache)
            stats = self._calculate_organization_stats(organization_id)
            cache.set(cache_key, stats, 60 * 10)  # Cache por 10 minutos
        
        return stats
    
    def _calculate_organization_stats(self, organization_id):
        """
        Cálculo real de estadísticas (sin cache)
        Esta función sería lenta sin Redis
        """
        from apps.users.models import User
        from apps.plans.models import Plan
        
        return {
            'total_users': User.objects.filter(organization_id=organization_id).count(),
            'active_users': User.objects.filter(
                organization_id=organization_id, 
                is_active=True
            ).count(),
            'current_plan': 'Pro',  # Esto vendría de la BD
            'last_updated': 'now'
        }
    
    def invalidate_organization_cache(self, organization_id):
        """
        Invalida todo el cache relacionado con una organización
        Útil cuando se actualizan datos importantes
        """
        cache_patterns = [
            f"org_data:{organization_id}:*",
            f"org_stats:{organization_id}",
            f"user_perms:*:{organization_id}:*"
        ]
        
        # Django-redis permite eliminar por patrón
        for pattern in cache_patterns:
            cache.delete_pattern(pattern)

# Funciones de utilidad específicas para el proyecto
def cache_plans_list(timeout=60*60):  # 1 hora
    """
    Cachea la lista de planes disponibles
    Los planes no cambian frecuentemente
    """
    cache_key = "available_plans"
    plans = cache.get(cache_key)
    
    if plans is None:
        from apps.plans.models import Plan
        plans = list(Plan.objects.filter(is_active=True).values(
            'id', 'name', 'price', 'max_users', 'features'
        ))
        cache.set(cache_key, plans, timeout)
    
    return plans

def cache_user_organization_context(user_id, timeout=60*15):
    """
    Cachea el contexto de organización del usuario
    Evita consultas repetidas en cada request
    """
    cache_key = f"user_org_context:{user_id}"
    context = cache.get(cache_key)
    
    if context is None:
        from apps.accounts.models import User
        try:
            user = User.objects.select_related('organization').get(id=user_id)
            context = {
                'organization_id': user.organization.id if user.organization else None,
                'organization_name': user.organization.name if user.organization else None,
                'user_role': 'admin',  # Esto vendría del modelo
                'permissions': ['read', 'write', 'delete']  # Ejemplo
            }
        except User.DoesNotExist:
            context = None
        
        cache.set(cache_key, context, timeout)
    
    return context

# Rate limiting con Redis
def rate_limit_user_actions(max_actions=100, window_seconds=3600):
    """
    Limita acciones por usuario usando Redis
    Útil para API endpoints o acciones sensibles
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return func(request, *args, **kwargs)
            
            user_id = request.user.id
            cache_key = f"rate_limit:{user_id}:{func.__name__}"
            
            # Obtener contador actual
            current_count = cache.get(cache_key, 0)
            
            if current_count >= max_actions:
                from django.http import HttpResponseTooManyRequests
                return HttpResponseTooManyRequests(
                    "Too many requests. Try again later."
                )
            
            # Incrementar contador
            cache.set(cache_key, current_count + 1, window_seconds)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator 