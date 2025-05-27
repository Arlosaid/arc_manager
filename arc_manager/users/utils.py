import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site


def generate_random_password(length=12):
    """
    Genera una contraseña aleatoria con caracteres seguros.
    
    Args:
        length (int): Longitud de la contraseña (por defecto 12)
        
    Returns:
        str: Contraseña aleatoria generada
    """
    # Definir los caracteres permitidos (excluyendo caracteres confusos)
    lowercase = 'abcdefghijkmnpqrstuvwxyz'  # Sin 'l' y 'o'
    uppercase = 'ABCDEFGHIJKMNPQRSTUVWXYZ'  # Sin 'I' y 'O'
    digits = '23456789'  # Sin '0' y '1'
    special = '@#$%&*+'  # Caracteres especiales seguros
    
    # Asegurar que la contraseña tenga al menos un carácter de cada tipo
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Completar el resto de la contraseña
    all_chars = lowercase + uppercase + digits + special
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Mezclar los caracteres para evitar patrones predecibles
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def send_new_user_email(user, password, request=None):
    """
    Envía un email al nuevo usuario con sus credenciales de acceso.
    
    Args:
        user: Instancia del modelo User
        password (str): Contraseña temporal generada
        request: Request HTTP actual (opcional, para obtener el dominio)
        
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        # Obtener el dominio del sitio
        if request:
            current_site = get_current_site(request)
            domain = current_site.domain
            protocol = 'https' if request.is_secure() else 'http'
        else:
            domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
            protocol = 'http'
        
        # URL de login
        login_url = f"{protocol}://{domain}{reverse('accounts:login')}"
        
        # Contexto para el template
        context = {
            'user': user,
            'password': password,
            'login_url': login_url,
            'site_name': getattr(settings, 'SITE_NAME', 'ARCH MANAGER'),
            'protocol': protocol,
            'domain': domain,
        }
        
        # Renderizar el contenido del email
        subject = f'Bienvenido a {context["site_name"]} - Credenciales de Acceso'
        
        # Email en HTML
        html_message = render_to_string('users/emails/new_user_credentials.html', context)
        
        # Email en texto plano (fallback)
        plain_message = render_to_string('users/emails/new_user_credentials.txt', context)
        
        # Enviar el email
        success = send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@archmanager.local'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return success
        
    except Exception as e:
        # Log del error (podrías usar logging aquí)
        print(f"Error enviando email a {user.email}: {str(e)}")
        return False


def send_password_changed_notification(user, request=None):
    """
    Envía una notificación cuando el usuario cambia su contraseña.
    
    Args:
        user: Instancia del modelo User
        request: Request HTTP actual (opcional)
        
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        # Obtener el dominio del sitio
        if request:
            current_site = get_current_site(request)
            domain = current_site.domain
            protocol = 'https' if request.is_secure() else 'http'
        else:
            domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
            protocol = 'http'
        
        # Contexto para el template
        context = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'ARCH MANAGER'),
            'protocol': protocol,
            'domain': domain,
        }
        
        # Renderizar el contenido del email
        subject = f'Contraseña cambiada en {context["site_name"]}'
        
        # Email en HTML
        html_message = render_to_string('users/emails/password_changed_notification.html', context)
        
        # Email en texto plano (fallback)
        plain_message = render_to_string('users/emails/password_changed_notification.txt', context)
        
        # Enviar el email
        success = send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@archmanager.local'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return success
        
    except Exception as e:
        # Log del error
        print(f"Error enviando notificación de cambio de contraseña a {user.email}: {str(e)}")
        return False 