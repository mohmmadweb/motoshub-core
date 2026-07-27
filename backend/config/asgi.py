import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django_asgi_app = get_asgi_application()

# WebSocket routing (chat/realtime) is layered on once the chat app lands.
application = django_asgi_app
