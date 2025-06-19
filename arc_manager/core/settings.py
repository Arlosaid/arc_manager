import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-^nqywk9lip*o%!y_jo3w)--_+yo5c&m-q^sw3dk*8(_k@%o4j4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Configuración mejorada para AWS Beanstalk
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Simplificar para deployment
if '*' in ALLOWED_HOSTS or os.environ.get('AWS_EXECUTION_ENV'):
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'core',
    'apps.accounts',
    'apps.main',
    'apps.orgs',
    'apps.users',
    'apps.plans',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'apps.accounts.middleware.LoginRequiredMiddleware',
    'apps.accounts.middleware.SuperuserRestrictMiddleware',
    'apps.orgs.middleware.OrganizationContextMiddleware',
]

ROOT_URLCONF = 'core.urls'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'axes.backends.AxesBackend',
]

# Configuración completa de Django Axes
# Configuración básica
AXES_ENABLED = True  # Habilitar Django Axes
AXES_FAILURE_LIMIT = 10  # Número de intentos fallidos antes de bloqueo
AXES_COOLOFF_TIME = 0.25  # Tiempo de bloqueo en horas
AXES_RESET_ON_SUCCESS = True  # Resetear contador al iniciar sesión correctamente

# Campos de formulario
AXES_USERNAME_FORM_FIELD = 'username'  # Nombre del campo que contiene el usuario/email
AXES_PASSWORD_FORM_FIELD = 'password'  # Nombre del campo de contraseña

# Configuración de manipulación y almacenamiento
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'  # Usar base de datos para almacenar intentos
AXES_LOCKOUT_BY_USER_OR_IP = True  # Bloquea por usuario o IP (nueva configuración)

# URLs y redirecciones
AXES_LOCKOUT_URL = '/accounts/login/?locked=1'  # URL a la que redirigir cuando se bloquea
AXES_REDIRECT_URL = '/accounts/login/'  # URL de redirección genérica

# Parámetros de bloqueo
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address', 'user_agent']  # Define qué parámetros usar para bloqueo
AXES_LOCKOUT_TEMPLATE = None  # No usar plantilla personalizada para bloqueos

# Configuración para excluir rutas específicas
AXES_ENABLE_ADMIN = False  # Desactivar Axes para el panel de admin
#AXES_WHITELIST_CALLABLE = 'core.utils.axes_whitelist'  # Función para lista blanca

# Configuración de mensajes y respuestas
AXES_LOCKOUT_CALLABLE = None  # No usar función personalizada para bloqueos
AXES_VERBOSE = True  # Mensaje verboso en los logs


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

import dj_database_url

# Configuración de base de datos con PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de WhiteNoise para archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/accounts/login/'  # URL a la que se redirige si se necesita iniciar sesión
LOGIN_REDIRECT_URL = '/main/'  # Redirigir al dashboard después del login
LOGOUT_REDIRECT_URL = '/accounts/login/' # Redirigir a la URL de login correcta

# URLs exentas (usando patrones regex)
LOGIN_EXEMPT_URLS = [
    r'^accounts/login/?$',
    r'^accounts/logout/?$',
    r'^accounts/password_reset/?$',
    r'^accounts/password_reset/done/?$',
    r'^accounts/reset/(.+)/(.+)/?$',  # Para las URLs de reset con token y uid
    r'^accounts/reset/done/?$',
    r'^admin/.*$',
    r'^static/.*$',  # Para los archivos estáticos
    r'^media/.*$',   # Para los archivos multimedia
]

# En producción, habilita estas configuraciones:
# SESSION_COOKIE_SECURE = True  # Requiere HTTPS
# CSRF_COOKIE_SECURE = True  # Requiere HTTPS

# Configuración de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = False
# Configuración adicional de seguridad para sesiones
SESSION_COOKIE_HTTPONLY = True  # Evita que JavaScript pueda acceder a la cookie (protección contra XSS)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La sesión termina cuando se cierra el navegador
SESSION_COOKIE_AGE = 1209600  # Tiempo de vida máximo de la sesión (2 semanas en segundos)
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección contra ataques CSRF

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'ignore_static_requests': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'static' not in record.getMessage(),
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true', 'ignore_static_requests'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/debug.log'),
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración del sitio
SITE_NAME = 'ARC Manager'
SITE_DOMAIN = 'localhost:8000'  # Cambiar en producción

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo
# Configuración para producción (descomentar y configurar cuando sea necesario)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu_correo@gmail.com'
# EMAIL_HOST_PASSWORD = 'tu_contraseña_de_aplicación'

# Configuración de correo para el sistema
DEFAULT_FROM_EMAIL = f'{SITE_NAME} <noreply@{SITE_DOMAIN}>'
SERVER_EMAIL = f'admin@{SITE_DOMAIN}'
ADMINS = [('Admin', 'admin@example.com')]  # Cambiar en producción

if DEBUG:
    # Para desarrollo: mostrar emails en la consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    DEFAULT_FROM_EMAIL = 'ARC MANAGER <noreply@archmanager.local>'
else:
    # Para producción: usar Amazon SES
    EMAIL_BACKEND = 'django_ses.SESBackend'
    
    # Configuración AWS SES
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION', 'us-east-1')
    AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
    
    # Configuración adicional para SES
    AWS_SES_AUTO_THROTTLE = 0.5  # Controlar la velocidad de envío
    AWS_SES_CONFIGURATION_SET = os.environ.get('AWS_SES_CONFIGURATION_SET')  # Opcional
    
    # Email verificado en SES
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@tudominio.com')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Configuración para el sistema de pagos
PAYMENT_BANK_INFO = {
    'bank_name': 'Banco BBVA',
    'account_holder': 'TU EMPRESA SA DE CV',
    'account_number': '0123456789',
    'clabe': '012345678901234567',
    'concept_prefix': 'Upgrade-Plan'
}

# Email del administrador para notificaciones de pagos
ADMIN_EMAIL = 'admin@tudominio.com'

# URL del sitio para enlaces en emails
SITE_URL = 'http://localhost:8000' if DEBUG else 'https://tudominio.com'

# ========================================
# CONFIGURACIONES ESPECÍFICAS PARA AWS BEANSTALK
# ========================================

# Detectar si estamos en AWS Beanstalk
IS_AWS_ENVIRONMENT = os.environ.get('AWS_EXECUTION_ENV') is not None

if IS_AWS_ENVIRONMENT:
    # Configuraciones específicas para producción en AWS
    
    # Forzar HTTPS en producción
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Configuración de cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Configuración de archivos estáticos para AWS
    # Si usas S3 para archivos estáticos, descomenta y configura:
    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    # AWS_S3_REGION_NAME = os.environ.get('AWS_REGION', 'us-east-1')
    # AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Configuración de logging para AWS CloudWatch
    LOGGING['handlers']['cloudwatch'] = {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django']['handlers'].append('cloudwatch')
    
    # Email con Amazon SES - ACTIVADO PARA PRODUCCIÓN
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION', 'us-east-1')
    AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'
    AWS_SES_AUTO_THROTTLE = 0.5
    
    # Override del email por defecto para AWS
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@tudominio.com')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    
    # Configuración de base de datos para RDS
    # NOTA: La configuración de RDS ya se maneja por DATABASE_URL arriba
    # if 'RDS_HOSTNAME' in os.environ:
    #     DATABASES['default'] = {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': os.environ['RDS_DB_NAME'],
    #         'USER': os.environ['RDS_USERNAME'],
    #         'PASSWORD': os.environ['RDS_PASSWORD'],
    #         'HOST': os.environ['RDS_HOSTNAME'],
    #         'PORT': os.environ['RDS_PORT'],
    #         'OPTIONS': {
    #             'connect_timeout': 60,
    #             'sslmode': 'require',
    #         },
    #     }
    
    # Configuración de cache con ElastiCache Redis (opcional)
    if os.environ.get('REDIS_ENDPOINT'):
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': f"redis://{os.environ.get('REDIS_ENDPOINT')}:6379/1",
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
    
    # Configuración para health check de Beanstalk
    HEALTH_CHECK_URL = '/health/'
    
    print("🚀 Configuración AWS Beanstalk activada")

else:
    print("🏠 Ejecutándose en ambiente local")

# Health check endpoint para AWS Beanstalk
def health_check(request):
    """Endpoint simple para health check de AWS"""
    from django.http import JsonResponse
    return JsonResponse({'status': 'healthy', 'service': 'arc-manager'})