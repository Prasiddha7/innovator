import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = os.getenv("DEBUG", "True") == "True"

# parse hosts string and remove empties
_raw_allowed = os.getenv("ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [h for h in _raw_allowed.split(",") if h]
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must be set when DEBUG is False")

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': int(os.getenv("DB_PORT", 5432)),
    }
}

# Other settings (simplified)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    # your apps here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'social_media_service.urls'
WSGI_APPLICATION = 'social_media_service.wsgi.application'

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Innovator Social Media Service API',
    'DESCRIPTION': 'API documentation for Social Media Service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
