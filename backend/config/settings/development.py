"""Development settings."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Browsable API is handy locally.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "apps.core.renderers.EnvelopeJSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

CORS_ALLOW_ALL_ORIGINS = True

# No Redis needed for local dev: in-memory cache + eager Celery.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CELERY_TASK_ALWAYS_EAGER = True

# In-memory channel layer for local dev (no Redis needed).
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
