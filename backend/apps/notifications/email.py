"""
Email delivery for notifications.

Sending is best-effort and never blocks the request that triggered it: Celery
delivers when a broker is configured, otherwise we fall back to sending inline.
With no SMTP host configured Django uses the console backend, so development
prints the mail instead of failing.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject: str, body: str, to: list[str]) -> None:
    if not to:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=True)
    except Exception:  # a broken mail server must never break the app
        logger.warning("email delivery failed", exc_info=True)


def notify_mention(message, mentioned_users) -> None:
    """Someone was @mentioned in a group conversation."""
    group = getattr(getattr(message.channel, "group", None), "name", "گفتگو")
    author = getattr(message.author, "name", "کاربر")
    recipients = [u.email for u in mentioned_users if u.email and u.id != message.author_id]
    _send(
        subject=f"[موتوشاب] {author} شما را در «{group}» منشن کرد",
        body=f"{author} در گروه «{group}» شما را منشن کرد:\n\n{message.text}\n",
        to=recipients,
    )


def notify_direct_message(dm) -> None:
    """A direct message arrived for someone who is not looking at the app."""
    if not dm.recipient.email:
        return
    _send(
        subject=f"[موتوشاب] پیام تازه از {dm.sender.name}",
        body=f"{dm.sender.name} برای شما پیام فرستاد:\n\n{dm.text}\n",
        to=[dm.recipient.email],
    )
