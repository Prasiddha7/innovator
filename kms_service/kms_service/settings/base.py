import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"
ALLOWED_HOSTS = ["*"]

SHARED_JWT_SECRET = os.getenv("SHARED_JWT_SECRET", "innovator-django-secret-key-shared-microservices-12345")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "kms",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "kms_service.urls"
WSGI_APPLICATION = "kms_service.wsgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME", "kms_db"),
        'USER': os.getenv("DB_USER", "innovator_user"),
        'PASSWORD': os.getenv("DB_PASSWORD", "Nep@tronix9335%"),
        'HOST': os.getenv("DB_HOST", "kms_db"),
        'PORT': int(os.getenv("DB_PORT", 5432)),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'kms.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SHARED_JWT_SECRET,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

AUTH_USER_MODEL = 'kms.User'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Innovator KMS Service API',
    'DESCRIPTION': 'API documentation for KMS Service',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JAZZMIN_SETTINGS = {
    "site_title": "Innovator Admin",
    "site_header": "Innovator",
    "site_brand": "Innovator KMS",
    "site_logo": "kms/logo.png",  # Make sure this exists or remove
    "welcome_sign": "Welcome to Innovator KMS Administration",
    "copyright": "Innovator Ltd",
    "search_model": ["kms.User", "kms.Teacher"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "kms.User"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["kms", "auth"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "kms.User": "fas fa-user-shield",
        "kms.School": "fas fa-school",
        "kms.ClassRoom": "fas fa-chalkboard",
        "kms.Teacher": "fas fa-chalkboard-teacher",
        "kms.Student": "fas fa-user-graduate",
        "kms.Course": "fas fa-book",
        "kms.Enrollment": "fas fa-user-plus",
        "kms.TeacherAttendance": "fas fa-calendar-check",
        "kms.StudentAttendance": "fas fa-clipboard-check",
        "kms.TeacherKYC": "fas fa-id-card",
        "kms.Coordinator": "fas fa-user-tie",
        "kms.TeacherSalary": "fas fa-money-bill-wave",
        "kms.TeacherSalarySlip": "fas fa-file-invoice-dollar",
        "kms.TeacherInvoice": "fas fa-file-invoice",
        "kms.CoordinatorInvoice": "fas fa-file-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"kms.User": "collapsible", "kms.Teacher": "vertical_tabs"},
}

JAZZMIN_UI_CONFIG = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

