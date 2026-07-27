from django.db import models

from apps.core.models import TenantScopedModel


class ResearchStage(models.TextChoices):
    OPEN = "open", "فراخوان باز"
    REVIEW = "review", "بررسی درخواست‌ها"
    JUDGING = "judging", "داوری"
    RUNNING = "running", "در حال اجرا"
    CLOSED = "closed", "پایان‌یافته"


class ResearchOpportunity(TenantScopedModel):
    title = models.CharField(max_length=300)
    field = models.CharField(max_length=200, blank=True)
    stage = models.CharField(max_length=8, choices=ResearchStage.choices, default=ResearchStage.OPEN)
    budget = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    supervisor = models.CharField(max_length=200, blank=True)
    deadline = models.DateField(null=True, blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="research")

    class Meta(TenantScopedModel.Meta):
        db_table = "research_opportunity"

    @property
    def applicant_count(self) -> int:
        return self.applications.count()


class ApplicationStatus(models.TextChoices):
    REVIEW = "review", "در بررسی"
    ACCEPTED = "accepted", "پذیرفته"
    REJECTED = "rejected", "رد شده"


class ResearchApplication(TenantScopedModel):
    opportunity = models.ForeignKey(ResearchOpportunity, on_delete=models.CASCADE, related_name="applications")
    applicant_name = models.CharField(max_length=200)
    affiliation = models.CharField(max_length=200, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=ApplicationStatus.choices, default=ApplicationStatus.REVIEW)

    class Meta(TenantScopedModel.Meta):
        db_table = "research_application"
