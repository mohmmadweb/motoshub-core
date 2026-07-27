from django.db import models

from apps.core.models import TenantScopedModel


class ChannelType(models.TextChoices):
    PUBLIC = "public", "عمومی"
    PRIVATE = "private", "خصوصی"


class Channel(TenantScopedModel):
    name = models.CharField(max_length=200)
    topic = models.CharField(max_length=300, blank=True)
    channel_type = models.CharField(max_length=8, choices=ChannelType.choices, default=ChannelType.PUBLIC)
    category = models.CharField(max_length=120, blank=True)
    owner = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="owned_channels")

    class Meta(TenantScopedModel.Meta):
        db_table = "chat_channel"

    def __str__(self):
        return self.name


class Message(TenantScopedModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="chat_messages")
    text = models.TextField()
    pinned = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "chat_message"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["channel", "created_at"])]
