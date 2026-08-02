"""Helper to create notifications from anywhere in the app."""
from .models import Notification


def notify(user, text, kind="system", link="", tenant=None):
    if user is None:
        return None
    return Notification.objects.create(
        user=user, text=text, kind=kind, link=link,
        tenant=tenant or getattr(user, "tenant", None),
    )
