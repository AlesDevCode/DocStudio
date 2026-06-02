# backend/core_docs/settings.py
from pathlib import Path
import os

# 1. Rutas del Proyecto (Define la raíz del directorio backend)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configuraciones de Desarrollo (¡Mantener seguro en producción!)
SECRET_KEY = 'django-insecure-cambia-esto-por-algo-seguro-en-el-futuro'
DEBUG = True
ALLOWED_HOSTS = []

# 3. Registro de Aplicaciones (Aquí mapeamos tu carpeta apps/)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus aplicaciones empaquetadas
    'apps.dividir',
    # 'apps.convertir', # Descoméntala cuando crees esta app
]

# 4. Middlewares de Seguridad y Control
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_docs.urls'

# 5. Configuración del Motor de Plantillas (Frontend)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Cambiado aquí para buscar en la raíz de DocStudio/frontend
        'DIRS': [os.path.join(BASE_DIR.parent, 'frontend')], 
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

WSGI_APPLICATION = 'core_docs.wsgi.application'

# 6. Base de Datos Local (El archivo db.sqlite3 que se creará solo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. Validación de Contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. Internacionalización (Configurado en Español)
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 9. Configuración de Archivos Estáticos (CSS, JS, IMAGENES)
STATIC_URL = 'static/'

# backend/core_docs/settings.py
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'css',
    BASE_DIR.parent / 'frontend' / 'js',
    BASE_DIR.parent / 'frontend' / 'img',
    BASE_DIR.parent / 'frontend' / 'includes', # Asegúrate de tener esta línea
]

# 10. Almacenamiento Local de Documentos (Media)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Tipo de campo autoincremental por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirecciones del sistema de Usuarios
LOGIN_URL = '/admin/login/'  # Temporalmente usa el de Django hasta que hagas tu login propio
LOGIN_REDIRECT_URL = 'panel_usuario'