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
