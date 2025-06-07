# middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
import re

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que son accesibles sin autenticación
        self.exempt_urls = [re.compile(url) for url in getattr(settings, 'LOGIN_EXEMPT_URLS', [])]
        # URL de login
        self.login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')

    def __call__(self, request):
        # Primero procesamos el request para cualquier otra middleware
        response = self.get_response(request)
        
        # Si ya estamos en una URL exenta o el usuario está autenticado, permitimos continuar
        if request.user.is_authenticated:
            return response
            
        path = request.path_info.lstrip('/')
        
        # Si estamos en la URL de login u otra URL exenta, permitimos continuar
        if path == self.login_url.lstrip('/') or any(pattern.match(path) for pattern in self.exempt_urls):
            return response
        
        # En cualquier otro caso, redirigimos al login
        return redirect(self.login_url)


class SuperuserRestrictMiddleware:
    """Middleware que bloquea el acceso de superusers a la aplicación y los redirige al admin"""
    
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
        # Si el usuario está autenticado y es superuser
        if (request.user.is_authenticated and 
            request.user.is_superuser and 
            not self._is_exempt_url(request.path_info.lstrip('/'))):
            
            messages.warning(
                request, 
                "Los superusuarios solo pueden acceder al panel administrativo de Django."
            )
            return redirect('/admin/')
        
        response = self.get_response(request)
        return response
    
    def _is_exempt_url(self, path):
        """Verifica si la URL está exenta del bloqueo de superuser"""
        return any(pattern.match(path) for pattern in self.exempt_urls)