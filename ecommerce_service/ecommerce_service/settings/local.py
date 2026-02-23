# ecommerce_service/settings/local.py
from datetime import timedelta
import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Shared secret for JWT verification across all microservices
SHARED_JWT_SECRET = os.getenv(
    "SHARED_JWT_SECRET",
    "innovator-django-secret-key-shared-microservices-12345"
)

SECRET_KEY = SHARED_JWT_SECRET

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'ecommerce',
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SHARED_JWT_SECRET,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
