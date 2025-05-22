from pathlib import Path
import os

# 1. Configuración de rutas base
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Seguridad (¡No exponer `SECRET_KEY` directamente!)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "valor_por_defecto_inseguro")
DEBUG = True  # Cambiar a False en producción
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# 3. Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',  # Para estilos Bootstrap
    'rest_framework',  # API REST
    'tienda',  # App principal
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

# 5. Configuración de URLs y templates
ROOT_URLCONF = 'ferremas_core.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tienda/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tienda.context_processors.carrito',
            ],
        },
    },
]

# 6. Base de datos (SQLite por defecto, opción PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si deseas usar PostgreSQL en el futuro:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'nombre_bd',
#         'USER': 'usuario',
#         'PASSWORD': 'contraseña',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# 7. Configuración de Django REST Framework (DRF)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Cambiar a 'IsAuthenticated' en producción
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# 8. Archivos estáticos y multimedia
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 9. Configuración de email (Para pruebas en desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 10. Configuración de sesiones
SESSION_COOKIE_AGE = 86400  # 1 día en segundos
SESSION_SAVE_EVERY_REQUEST = True

# 11. Configuración de Webpay Plus (Modo TEST)
TRANSBANK_WEBPAY = {
    'COMMERCE_CODE': '597020000541',  # Código de prueba correcto
    'API_KEY': '597020000541',  # ✅ Usa el mismo código en modo TEST
    'ENVIRONMENT': 'TEST',  # ✅ Confirmar que esté en entorno de prueba
}