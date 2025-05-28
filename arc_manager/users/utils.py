import string
import random
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def generate_random_password(length=12):
    """
    Genera una contraseña aleatoria segura con la longitud especificada.
    La contraseña incluye mayúsculas, minúsculas, números y caracteres especiales.
    """
    # Definir los conjuntos de caracteres
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    # Caracteres especiales más seguros y fáciles de usar
    special = '!@#$%&*'
    
    # Asegurar al menos un carácter de cada tipo
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # Completar el resto de la contraseña con caracteres aleatorios
    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # Mezclar los caracteres
    random.shuffle(password)
    
    # Convertir la lista a string
    return ''.join(password)

def send_new_user_email(user, password, request=None):
    """
    Envía un email al nuevo usuario con sus credenciales de acceso.
    Retorna True si el email se envió correctamente, False en caso contrario.
    """
    try:
        # Preparar el contexto para el template
        context = {
            'user': user,
            'password': password,
            'site_name': settings.SITE_NAME,
            'site_url': request.build_absolute_uri('/') if request else settings.SITE_URL
        }
        
        # Renderizar el template
        message = render_to_string('users/emails/new_user_credentials.html', context)
        
        # Enviar el email
        send_mail(
            subject=f'Bienvenido a {settings.SITE_NAME} - Tus credenciales de acceso',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return True
    except Exception as e:
        print(f"Error al enviar email: {str(e)}")
        return False 