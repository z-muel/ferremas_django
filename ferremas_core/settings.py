"""
Configuración Django para proyecto Ferremas Core

Optimizado para:
- Desarrollo local (DEBUG=True)
- API REST con DRF
- Sistema de archivos estáticos y multimedia
- Configuración regional chilena
"""

from pathlib import Path

# 1. Configuración de rutas base
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Seguridad (¡Cambiar en producción!)
SECRET_KEY = 'django-insecure-@4+o(kyi_86c+1$@jpg9)@o@v!pd@&8&s1qptb^0upcf_tl@to'  # ¡Regenerar en producción!
DEBUG = True  # Desactivar en producción
ALLOWED_HOSTS = []  # Agregar dominios en producción

# 3. Aplicaciones instaladas
INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django_bootstrap5',  # Para estilos Bootstrap
    'rest_framework',     # Para API REST
    
    # Local apps
    'tienda',  # Tu app principal
]

# 4. Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5. URLs y templates
ROOT_URLCONF = 'ferremas_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tienda/templates'],  # Busca templates en esta carpeta
        'APP_DIRS': True,  # Busca templates en cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tienda.context_processors.carrito',  # ¡Añadir para contexto del carrito!
            ],
        },
    },
]

# 6. Base de datos (SQLite para desarrollo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. Configuración regional (Chile)
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# 9. Archivos estáticos y multimedia
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Desarrollo
# STATIC_ROOT = BASE_DIR / 'staticfiles'  # ¡Descomentar para producción!

MEDIA_URL = '/media/'  # Archivos subidos por usuarios
MEDIA_ROOT = BASE_DIR / 'media'

# 10. Configuración DRF (API REST)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Temporal - cambiar en producción
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# 11. Configuración de sesiones (para carrito)
SESSION_COOKIE_AGE = 86400  # 1 día en segundos
SESSION_SAVE_EVERY_REQUEST = True

# 12. Configuración de email (para desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Imprime emails en consola