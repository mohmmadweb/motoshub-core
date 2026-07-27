"""Admin/console: per-tenant workflow parameters + branding (SettingsContext)."""
from django.db import models

from apps.core.models import TimeStampedModel


class WorkflowSettings(TimeStampedModel):
    """One row per tenant — mirrors the prototype's SettingsContext defaults."""

    tenant = models.OneToOneField("tenancy.Tenant", on_delete=models.CASCADE, related_name="workflow_settings")

    report_reminder_days = models.PositiveSmallIntegerField(default=7)
    review_escalation_days = models.PositiveSmallIntegerField(default=15)
    dormant_project_days = models.PositiveSmallIntegerField(default=30)
    screening_threshold = models.PositiveSmallIntegerField(default=80)
    jury_threshold = models.PositiveSmallIntegerField(default=50)
    legal_review_days = models.PositiveSmallIntegerField(default=7)
    retention_percent = models.PositiveSmallIntegerField(default=10)
    prepayment_percent = models.PositiveSmallIntegerField(default=25)
    rate_limit_per_minute = models.PositiveSmallIntegerField(default=60)
    edit_window_count = models.PositiveSmallIntegerField(default=1)

    # Branding.
    accent = models.CharField(max_length=32, default="brand")
    font_scale = models.CharField(max_length=8, default="normal")  # normal|large
    dark_default = models.BooleanField(default=False)
    enabled_modules = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "console_workflow_settings"
