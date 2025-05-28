from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.cache import cache
from .forms import CustomAuthenticationForm
import logging

logger = logging.getLogger('app')

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = CustomAuthenticationForm
    
    def form_valid(self, form):
        user = form.get_user()
        # Obtener información antes del login
        user_info = {
            'username': user.username or user.email,
            'role': user.role_display(),
            'organization': user.get_organization_name()
        }
        
        # Proceder con el login normal
        response = super().form_valid(form)
        
        # Registrar login exitoso
        logger.info(f"Login exitoso - Usuario: {user_info['username']}, Rol: {user_info['role']}, Organización: {user_info['organization']}")
        return response
    
    def form_invalid(self, form):
        # Registrar intento de login fallido
        username = form.cleaned_data.get('username', 'No especificado')
        logger.warning(f"Intento de login fallido para: {username}")
        return super().form_invalid(form)

class CustomLogoutView(View):
    """Vista personalizada para logout con logging"""
    
    def get(self, request, *args, **kwargs):
        return self.logout_user(request)
    
    def post(self, request, *args, **kwargs):
        return self.logout_user(request)
    
    def logout_user(self, request):
        # Capturar el nombre de usuario ANTES de hacer logout
        if request.user.is_authenticated:
            username = request.user.username or request.user.email
            role = request.user.role_display()
            organization = request.user.get_organization_name()
            
            logger.info(f"Logout - Usuario: {username}, Rol: {role}, Organización: {organization}")
        
        logout(request)
        return redirect('accounts:login')

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
            messages.info(self.request, "Ya enviamos instrucciones. Revisa tu correo o espera 15 minutos para solicitar otro.", extra_tags='password_reset')
            return self.form_invalid(form)
        
        # Guardar en cache por 15 minutos
        cache.set(cache_key, True, timeout=900)
        
        return super().form_valid(form)