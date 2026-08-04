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

# HTTPS on by default. A deployment that has not obtained a certificate yet must
# opt out explicitly (SECURE_SSL_REDIRECT=False) — otherwise every request would
# redirect to an https:// URL nothing is listening on. Secure cookies and HSTS
# follow the same switch: sending them over plain HTTP either breaks login (the
# browser withholds the cookie) or pins the host to HTTPS for a year.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
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
