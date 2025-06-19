# middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.http import HttpResponseServerError
from django.template import loader
import logging
import re

logger = logging.getLogger(__name__)

class LoginRequiredMiddleware:
    """
    Middleware que requiere autenticación para todas las vistas excepto las especificadas.
    
    Si un usuario no autenticado intenta acceder a una vista protegida,
    será redirigido a la página de login.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que son accesibles sin autenticación
        self.exempt_urls = [re.compile(url) for url in getattr(settings, 'LOGIN_EXEMPT_URLS', [])]
        # URL de login
        self.login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Verificar si la vista requiere autenticación.
        Si el usuario no está autenticado y la URL no está en la lista de excepciones,
        redirigir al login.
        """
        
        # Si el usuario ya está autenticado, continuar
        if request.user.is_authenticated:
            return None
        
        path = request.path_info.lstrip('/')
        
        # Verificar si la URL actual está en la lista de URLs exentas
        if path == self.login_url.lstrip('/') or any(pattern.match(path) for pattern in self.exempt_urls):
            return None  # Permitir acceso sin autenticación
        
        # Si llegamos aquí, redirigir al login
        return redirect(f'{self.login_url}?next={path}')


class SuperuserRestrictMiddleware:
    """
    Middleware para restringir acceso al admin panel solo a superusers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs exentas del bloqueo de superuser (admin, logout, etc.)
        self.exempt_urls = [
            re.compile(r'^admin/.*$'),
            re.compile(r'^accounts/logout/?$'),
            re.compile(r'^static/.*$'),
            re.compile(r'^media/.*$'),
        ]

    def __call__(self, request):
        # Verificar acceso al admin
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
            
            if not request.user.is_superuser:
                messages.error(request, "No tienes permisos para acceder al panel de administración.")
                return redirect('main:dashboard')
        
        response = self.get_response(request)
        return response
    
    def _is_exempt_url(self, path):
        """Verifica si la URL está exenta del bloqueo de superuser"""
        return any(pattern.match(path) for pattern in self.exempt_urls)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware para manejo de errores en producción.
    Evita que se muestren errores técnicos a los usuarios finales.
    """
    
    def process_exception(self, request, exception):
        """
        Procesar excepciones no capturadas
        """
        if not settings.DEBUG:
            # En producción, loggear el error y mostrar página amigable
            logger.error(
                f"Error no manejado en {request.path}: {str(exception)}",
                exc_info=True,
                extra={
                    'request': request,
                    'user': request.user if hasattr(request, 'user') else None,
                }
            )
            
            # Intentar cargar template personalizado de error
            try:
                template = loader.get_template('500.html')
                return HttpResponseServerError(template.render({}))
            except Exception:
                # Si falla el template, devolver respuesta básica
                return HttpResponseServerError(
                    "<h1>Error del Servidor</h1><p>Ha ocurrido un error interno. Por favor, contacta con soporte técnico.</p>"
                )
        
        # En desarrollo, dejar que Django maneje el error normalmente
        return None