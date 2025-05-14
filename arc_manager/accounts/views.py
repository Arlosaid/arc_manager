from django.contrib.auth.views import PasswordResetView
from django.core.cache import cache
from django.contrib import messages
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

# Inicializa el logger
logger = logging.getLogger('app')
security_logger = logging.getLogger('django.security')

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

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        """Método llamado cuando el formulario es válido"""
        # Autentica al usuario usando el backend de Django
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Registro de evento exitoso
            login(self.request, user)
            security_logger.info(f"Inicio de sesión exitoso para el usuario: {username}")
            logger.info(f"Usuario {username} ha iniciado sesión")
            return redirect(self.get_success_url())
        else:
            # Registro de evento fallido
            security_logger.warning(f"Intento de inicio de sesión fallido para el usuario: {username}")
            logger.warning(f"Intento de inicio de sesión fallido: {username}")
            messages.error(self.request, "Credenciales inválidas")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Método llamado cuando el formulario es inválido"""
        logger.warning(f"Formulario de inicio de sesión inválido: {form.errors}")
        return super().form_invalid(form)

class DashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        """Maneja las solicitudes GET"""
        logger.debug(f"Usuario {request.user} accedió al dashboard")
        return super().get(request, *args, **kwargs)