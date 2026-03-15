# social_media_service/settings/local.py
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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "social_media.authentication.CustomJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SHARED_JWT_SECRET,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "LEEWAY": timedelta(hours=1),
}
