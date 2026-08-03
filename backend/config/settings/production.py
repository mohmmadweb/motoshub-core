"""Production settings — hardened. Never runs with DEBUG on."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

# Refuse to boot with development secrets in production.
if SECRET_KEY == "insecure-dev-key":  # noqa: F405
    raise ImproperlyConfigured("SECRET_KEY must be set to a real value in production.")
if OW_PASSWORD_PEPPER == "shared-secret-must-match-php-backend":  # noqa: F405
    raise ImproperlyConfigured("OW_PASSWORD_PEPPER must be set (shared with the PHP backend) in production.")

# ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS / CORS_ALLOWED_ORIGINS come from the env.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
