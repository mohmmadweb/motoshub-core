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
    # A group's conversation is a channel, so groups reuse the whole chat stack
    # (messages, reactions, pins, realtime) instead of duplicating it.
    group = models.OneToOneField("social.Group", on_delete=models.CASCADE, null=True, blank=True,
                                 related_name="channel")

    class Meta(TenantScopedModel.Meta):
        db_table = "chat_channel"

    def __str__(self):
        return self.name


class Message(TenantScopedModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="chat_messages")
    text = models.TextField(blank=True)
    pinned = models.BooleanField(default=False)
    # ── Telegram-style message features ──────────────────────────────────────
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="replies")
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False, help_text="حذف نرم — «این پیام حذف شد»")
    forwarded_from = models.CharField(max_length=200, blank=True)
    attachment = models.JSONField(null=True, blank=True, help_text="{kind,name,size,url}")
    mentions = models.JSONField(default=list, blank=True, help_text="شناسهٔ کاربران منشن‌شده")
    topic = models.ForeignKey("social.GroupTopic", on_delete=models.CASCADE, null=True, blank=True,
                              related_name="messages", help_text="تاپیک گروه؛ خالی = فید اصلی")

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
