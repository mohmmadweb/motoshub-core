"""
Base settings — shared by every environment.

Design decisions (see docs/ARCHITECTURE.md):
* Greenfield, clean PostgreSQL schema (managed models) that fully models the
  demo.shub.ir prototype — NOT bound to the legacy Oxwall schema.
* Contract-compatible with the ecosystem: `{data, links, meta}` envelope, a
  uniform error body, and unified HS256 JWT signed with OW_PASSWORD_PEPPER so a
  token issued by the PHP backend validates here and vice-versa (Kong gateway).
"""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["*"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    JWT_ACCESS_TTL_MINUTES=(int, 30),
    JWT_REFRESH_TTL_DAYS=(int, 14),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# ── Applications ────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "channels",
]
# Local apps — one Django app per bounded context. Domain apps are appended as
# they are implemented; the ordering respects FK dependencies.
LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.tenancy",
    "apps.rbac",
    "apps.content",
    "apps.social",
    "apps.projects",
    "apps.contracts",
    "apps.fund",
    "apps.training",
    "apps.support",
    "apps.polls",
    "apps.research",
    "apps.awards",
    "apps.notifications",
    "apps.chat",
    "apps.console",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Resolves the active tenant from the JWT / X-Tenant header on every request.
    "apps.tenancy.middleware.CurrentTenantMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ── Database ────────────────────────────────────────────────────────────────
DATABASES = {"default": env.db("DATABASE_URL", default="postgres://motoshub:motoshub@localhost:5432/motoshub_core")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# ── Auth ────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── DRF ─────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.UnifiedJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "apps.core.renderers.EnvelopeJSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.EnvelopePagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.envelope_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ── Unified JWT (HS256, shared pepper with the PHP backend) ──────────────────
OW_PASSWORD_PEPPER = env("OW_PASSWORD_PEPPER", default="shared-secret-must-match-php-backend")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TTL = timedelta(minutes=env("JWT_ACCESS_TTL_MINUTES"))
JWT_REFRESH_TTL = timedelta(days=env("JWT_REFRESH_TTL_DAYS"))
JWT_ISSUER = "motoshub"

# ── Cache / Celery / Channels (Redis) ───────────────────────────────────────
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_TASK_ALWAYS_EAGER = False
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# ── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# ── i18n / tz (Persian, Tehran) ─────────────────────────────────────────────
LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# ── Static / media ──────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── OpenAPI ─────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Motoshub Core API",
    "DESCRIPTION": "Django backend for the Motoshub platform (api2 / motonextapi).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
