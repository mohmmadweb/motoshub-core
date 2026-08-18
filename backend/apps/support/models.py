from django.db import models

from apps.core.models import ScopedContentModel, TenantScopedModel


class Priority(models.TextChoices):
    LOW = "low", "کم"
    MEDIUM = "medium", "متوسط"
    URGENT = "urgent", "فوری"


class TicketStatus(models.TextChoices):
    OPEN = "open", "باز"
    IN_REVIEW = "in_review", "در حال بررسی"
    ANSWERED = "answered", "پاسخ داده شد"
    CLOSED = "closed", "بسته"


class Ticket(TenantScopedModel, ScopedContentModel):
    number = models.CharField(max_length=32, blank=True)
    subject = models.CharField(max_length=300)
    category = models.CharField(max_length=120, blank=True)
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=10, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="tickets")

    class Meta(TenantScopedModel.Meta):
        db_table = "support_ticket"

    def __str__(self):
        return self.subject


class TicketMessage(TenantScopedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="ticket_messages")
    from_support = models.BooleanField(default=False)
    body = models.TextField()

    class Meta(TenantScopedModel.Meta):
        db_table = "support_ticket_message"
        ordering = ["created_at"]
