from django.db import models

from apps.core.models import TenantScopedModel


class NotificationType(models.TextChoices):
    MENTION = "mention", "منشن"
    LIKE = "like", "پسند"
    COMMENT = "comment", "نظر"
    SYSTEM = "system", "سیستمی"
    TASK = "task", "وظیفه"


class Notification(TenantScopedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notifications")
    text = models.CharField(max_length=500)
    kind = models.CharField(max_length=10, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "notifications_notification"
        indexes = [models.Index(fields=["user", "read", "-created_at"])]
