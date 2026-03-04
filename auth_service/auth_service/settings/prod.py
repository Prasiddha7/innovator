from .base import *

DEBUG = False
_raw_allowed = os.environ.get("ALLOWED_HOSTS", "yourdomain.com")
ALLOWED_HOSTS = [
    "182.93.94.220",
    "localhost",
    "127.0.0.1",
]
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "innovator-django-secret-key-shared-microservices-12345"
)
   

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "auth_db",
        "USER": "innovator_user",
        "PASSWORD": "Nep@tronix9335%",
        "HOST": "auth_db",
        "PORT": "5432",
    }
}