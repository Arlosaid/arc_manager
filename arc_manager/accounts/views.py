from django.contrib.auth.views import PasswordResetView, LogoutView
from django.core.cache import cache
from django.contrib import messages
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

# Inicializa el logger
logger = logging.getLogger('app')
security_logger = logging.getLogger('django.security')

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def form_valid(self, form):
        """Método llamado cuando el formulario es válido"""
        # Obtener nombre de usuario (puede ser email o username)
        username = form.cleaned_data.get('username')
        
        # La autenticación la maneja la clase base LoginView
        response = super().form_valid(form)
        
        # Después de que LoginView ha hecho el login, registramos el éxito
        security_logger.info(f"Inicio de sesión exitoso para el usuario: {username}")
        logger.info(f"Usuario {username} ha iniciado sesión")
        
        return response

    def form_invalid(self, form):
        """Método llamado cuando el formulario es inválido"""
        # Intentar obtener el username del formulario (podría no estar si el formulario tiene errores)
        username = form.cleaned_data.get('username', 'desconocido')
        
        # Registrar el intento fallido
        security_logger.warning(f"Intento de inicio de sesión fallido para el usuario: {username}")
        logger.warning(f"Intento de inicio de sesión fallido: {username}")
        logger.warning(f"Formulario de inicio de sesión inválido: {form.errors}")
        
        # Añadir mensaje de error
        messages.error(self.request, "Credenciales inválidas")
        
        return super().form_invalid(form)
    
class CustomLogoutView(View):
    """Vista personalizada para el cierre de sesión que funciona con GET y POST"""
    
    def get(self, request, *args, **kwargs):
        return self.logout_user(request)
        
    def post(self, request, *args, **kwargs):
        return self.logout_user(request)
    
    def logout_user(self, request):
        # Capturar el nombre de usuario ANTES de hacer logout
        username = ""
        if request.user.is_authenticated:
            username = request.user.username or request.user.email or str(request.user.id)
            
        # Registrar el cierre de sesión con el nombre de usuario capturado
        security_logger.info(f"Cierre de sesión del usuario: {username}")
        logger.info(f"Usuario {username} ha cerrado sesión")
        
        # Realizar el logout después de capturar la información
        logout(request)
        
        # Redirigir al login
        return HttpResponseRedirect(reverse_lazy('accounts:login'))

class SecurePasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = '/accounts/password_reset/done/'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        cache_key = f"password_reset_{email}"
        
        # Verificar si ya hay una solicitud reciente
        if cache.get(cache_key):
            messages.info(self.request, "Ya enviamos instrucciones. Revisa tu correo o espera 15 minutos para solicitar otro.")
            return self.form_invalid(form)
        
        # Guardar en cache por 15 minutos
        cache.set(cache_key, True, timeout=900)
        
        return super().form_valid(form)