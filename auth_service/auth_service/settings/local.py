from datetime import timedelta
import os
from .base import *


# Shared secret for JWT signing across all microservices
SHARED_JWT_SECRET = os.getenv(
    "SHARED_JWT_SECRET",
    "innovator-django-secret-key-shared-microservices-12345"
)

SECRET_KEY = SHARED_JWT_SECRET
DEBUG = True
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "192.168.1.85",
    "unerratic-stanford-rimosely.ngrok-free.dev",]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "accounts",
    "corsheaders",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  
        "NAME": os.getenv("DB_NAME", "auth_db"),
        "USER": os.getenv("DB_USER", "innovator_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "Nep@tronix9335%"),
        "HOST": os.getenv("DB_HOST", "auth_db"),  # Must match Docker service name
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", 
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",         # MUST be before auth middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",      # Required for admin & auth
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # you can add template dirs here
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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# # Use the same secret as auth_service for HS256
# JWT_SECRET = "sB7!vT8x#rK2qL9@uF1zM3dP5yH0wE6c"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SHARED_JWT_SECRET,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOW_ALL_ORIGINS = True 

CSRF_TRUSTED_ORIGINS = [
    "https://unerratic-stanford-rimosely.ngrok-free.dev"
]