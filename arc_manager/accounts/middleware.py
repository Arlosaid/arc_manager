# middleware.py
from django.shortcuts import redirect
from django.conf import settings
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