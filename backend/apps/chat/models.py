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


class DirectMessage(TenantScopedModel):
    """One-to-one direct message. A "thread" is all messages between two users."""
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="dm_sent")
    recipient = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="dm_received")
    text = models.TextField()
    read = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "chat_direct_message"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["sender", "recipient", "created_at"])]


class MessageReaction(TenantScopedModel):
    """A user's reaction on a channel message (icon-based, matches the prototype)."""
    ICONS = [("ThumbsUp", "پسند"), ("Heart", "قلب"), ("Smile", "لبخند"), ("CheckCircle2", "تأیید")]
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="message_reactions")
    icon = models.CharField(max_length=16, choices=ICONS)

    class Meta(TenantScopedModel.Meta):
        db_table = "chat_message_reaction"
        constraints = [models.UniqueConstraint(fields=["message", "user", "icon"], name="uniq_message_reaction")]
