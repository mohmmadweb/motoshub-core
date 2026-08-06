"""Admin/console: per-tenant workflow parameters + branding (SettingsContext)."""
from django.db import models

from apps.core.models import TenantScopedModel, TimeStampedModel


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

    # ── System variables edited from «متغیرهای سیستم» ────────────────────────
    # Stored per tenant so they can change without a redeploy, which is exactly
    # what that panel claims. Each one is read at the point it applies.
    upload_max_mb = models.PositiveSmallIntegerField(default=100)
    chunk_size_mb = models.PositiveSmallIntegerField(default=10)
    user_quota_gb = models.PositiveSmallIntegerField(default=5)
    image_max_px = models.PositiveIntegerField(default=1920)
    session_hours = models.PositiveSmallIntegerField(default=24)
    login_attempts = models.PositiveSmallIntegerField(default=5)
    lock_minutes = models.PositiveSmallIntegerField(default=15)
    feed_page_size = models.PositiveSmallIntegerField(default=20)
    notif_batch = models.PositiveIntegerField(default=500)
    digest_hour = models.PositiveSmallIntegerField(default=8)
    maintenance_mode = models.BooleanField(default=False, help_text="فقط راهبران وارد شوند")

    # Branding.
    accent = models.CharField(max_length=32, default="brand")
    font_scale = models.CharField(max_length=8, default="normal")  # normal|large
    dark_default = models.BooleanField(default=False)
    enabled_modules = models.JSONField(default=list, blank=True)

    # Console configuration edited from the admin panel.
    admin_pages = models.JSONField(default=list, blank=True)
    allowed_file_extensions = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "console_workflow_settings"


class SavedReport(TenantScopedModel):
    """A report definition a user saved from the report builder."""
    SCHEDULES = [("none", "بدون زمان‌بندی"), ("weekly", "هفتگی"), ("monthly", "ماهانه")]
    name = models.CharField(max_length=300)
    module = models.CharField(max_length=120, blank=True)
    group_by = models.CharField(max_length=120, blank=True)
    schedule = models.CharField(max_length=8, choices=SCHEDULES, default="none")
    last_run = models.CharField(max_length=40, blank=True)
    format = models.CharField(max_length=12, default="Excel")

    class Meta(TenantScopedModel.Meta):
        db_table = "console_saved_report"

    def __str__(self):
        return self.name


class Integration(TenantScopedModel):
    """Webhook / bot / slash-command registered for a channel."""
    TYPES = [("in_webhook", "وب‌هوک ورودی"), ("out_webhook", "وب‌هوک خروجی"),
             ("bot", "بات"), ("slash", "دستور اسلش")]
    name = models.CharField(max_length=200)
    integration_type = models.CharField(max_length=12, choices=TYPES, default="in_webhook")
    channel = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=200, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "console_integration"

    def __str__(self):
        return self.name


class GuestAccount(TenantScopedModel):
    """External collaborator with time-boxed access to specific channels."""
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200, blank=True)
    channels = models.JSONField(default=list, blank=True)
    expires = models.CharField(max_length=20, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "console_guest_account"

    def __str__(self):
        return self.name
