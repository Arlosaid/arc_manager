import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^nqywk9lip*o%!y_jo3w)--_+yo5c&m-q^sw3dk*8(_k@%o4j4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
    'accounts',
    'main',
    'orgs',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'accounts.middleware.LoginRequiredMiddleware',
    'orgs.middleware.OrganizationMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/accounts/login/'  # URL a la que se redirige si se necesita iniciar sesión
LOGIN_REDIRECT_URL = '/main/'  # Redirigir al home después del login
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
            'level': 'WARNING',  # Solo mostrar warnings y errores
            'propagate': True,
        },
        'django.server': {
            'handlers': ['file'],  # Las solicitudes HTTP solo van al archivo
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['file', 'security_file'],  # Quita 'console'
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',  # O 'DEBUG' si necesitas más detalle
            'propagate': False,
        },
    },
}

if DEBUG:
    # Para desarrollo: mostrar emails en la consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    DEFAULT_FROM_EMAIL = 'ARCH MANAGER <noreply@archmanager.local>'
else:
    # Para producción: usar Amazon SES
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_ACCESS_KEY_ID = 'your-access-key'
    AWS_SECRET_ACCESS_KEY = 'your-secret-key'
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'