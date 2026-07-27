from django.db import models

from apps.core.models import TenantScopedModel


class AwardTrack(TenantScopedModel):
    title = models.CharField(max_length=200)
    categories = models.JSONField(default=list, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "awards_track"

    @property
    def submission_count(self) -> int:
        return self.entries.count()


class EntryStatus(models.TextChoices):
    SUBMITTED = "submitted", "ثبت‌شده"
    VALIDATING = "validating", "صحت‌سنجی هلدینگ"
    JUDGING = "judging", "در حال داوری"
    SCORED = "scored", "امتیازدهی شده"
    FINALIST = "finalist", "منتخب مرحله نهایی"


class AwardEntry(TenantScopedModel):
    track = models.ForeignKey(AwardTrack, on_delete=models.CASCADE, related_name="entries")
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=12, choices=EntryStatus.choices, default=EntryStatus.SUBMITTED)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    edit_used = models.BooleanField(default=False, help_text="ویرایش یک‌بارمصرف مصرف شد")

    class Meta(TenantScopedModel.Meta):
        db_table = "awards_entry"
