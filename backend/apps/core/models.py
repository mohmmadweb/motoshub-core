"""Shared model bases."""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """UUID pk + created/updated timestamps — the base for every domain model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantScopedModel(TimeStampedModel):
    """
    Base for content owned by a tenant. Row-level isolation is enforced by
    `TenantScopedQuerySet`/managers plus the CurrentTenantMiddleware — no query
    may cross tenants unless it explicitly opts out.
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True,
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True


class Visibility(models.TextChoices):
    PUBLIC = "public", "عمومی"
    PRIVATE = "private", "خصوصی"


class ContentScope(models.TextChoices):
    GLOBAL = "global", "سراسری"
    HOLDING = "holding", "هلدینگ"
    COMPANY = "company", "شرکت"


class ScopedContentModel(models.Model):
    """Content that belongs to a domain within the organisation.

    «سراسری» reaches everyone, «هلدینگ» reaches one holding's companies, and
    «شرکت» reaches a single subsidiary. The columns are only the declaration —
    enforcement is in TenantScopedModelViewSet, which filters every queryset by
    the caller's resolved scope so a subsidiary's content cannot be fetched by
    someone outside it.
    """
    scope = models.CharField(max_length=8, choices=ContentScope.choices, default=ContentScope.GLOBAL)
    holding = models.ForeignKey("tenancy.Holding", on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey("tenancy.Company", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True


class Attachment(TenantScopedModel):
    """A stored file. One model serves chat attachments, knowledge docs and media,
    so upload/serve/permission logic lives in exactly one place."""
    KINDS = [("photo", "تصویر"), ("doc", "سند"), ("audio", "صوت"), ("video", "ویدیو"), ("other", "سایر")]
    file = models.FileField(upload_to="uploads/%Y/%m/")
    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=8, choices=KINDS, default="other")
    size = models.PositiveIntegerField(default=0, help_text="بایت")
    content_type = models.CharField(max_length=120, blank=True)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True,
                                    related_name="attachments")
    # Generated preview for images; empty when the file is not an image or the
    # thumbnail has not been built yet.
    thumbnail = models.ImageField(upload_to="thumbs/%Y/%m/", blank=True, null=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "core_attachment"

    def __str__(self):
        return self.name

    @property
    def human_size(self) -> str:
        n = float(self.size)
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024 or unit == "GB":
                return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
            n /= 1024
        return f"{n:.1f}GB"


def thumbnail_path(attachment) -> str:
    """Where an attachment's thumbnail lives, derived from the original."""
    base, _, _ = attachment.file.name.rpartition(".")
    return f"{base or attachment.file.name}.thumb.jpg"
