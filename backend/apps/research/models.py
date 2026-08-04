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


# ── RFP (فراخوان فناور برتر) ────────────────────────────────────────────────
class RfpCall(TenantScopedModel):
    STAGES = [("publish", "انتشار فراخوان"), ("docs", "دریافت مستندات"),
              ("biz", "ارزیابی کسب‌وکاری"), ("tech", "ارزیابی فنی"),
              ("open", "بازگشایی پاکات"), ("selected", "فناور برتر انتخاب شد")]
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=200, blank=True)
    holding = models.CharField(max_length=200, blank=True)
    stage = models.CharField(max_length=10, choices=STAGES, default="publish")
    deadline = models.CharField(max_length=20, blank=True, help_text="مهلت (جلالی نمایشی)")
    channels = models.JSONField(default=list, blank=True, help_text="محل‌های انتشار")

    class Meta(TenantScopedModel.Meta):
        db_table = "research_rfp_call"

    def __str__(self):
        return self.title


class RfpVendor(TenantScopedModel):
    call = models.ForeignKey(RfpCall, on_delete=models.CASCADE, related_name="vendors")
    name = models.CharField(max_length=200)
    biz_score = models.PositiveSmallIntegerField(null=True, blank=True)
    tech_score = models.PositiveSmallIntegerField(null=True, blank=True)
    price_opened = models.BooleanField(default=False)
    price = models.CharField(max_length=80, blank=True)
    winner = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "research_rfp_vendor"


# ── فرصت مطالعاتی اساتید ────────────────────────────────────────────────────
class Sabbatical(TenantScopedModel):
    STAGES = [("call", "فراخوان"), ("select", "انتخاب استاد"), ("contract", "قرارداد"),
              ("running", "در حال اجرا"), ("final", "کتابچه و ارائه نهایی"), ("closed", "خاتمه")]
    professor = models.CharField(max_length=200)
    university = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=200, blank=True, help_text="شرکت صنعتی میزبان")
    topic = models.CharField(max_length=300)
    trl_before = models.PositiveSmallIntegerField(default=0)
    trl_after = models.PositiveSmallIntegerField(null=True, blank=True)
    contract = models.CharField(max_length=120, blank=True)
    stage = models.CharField(max_length=10, choices=STAGES, default="call")

    class Meta(TenantScopedModel.Meta):
        db_table = "research_sabbatical"

    def __str__(self):
        return f"{self.professor} — {self.topic}"


class SabbaticalReport(TenantScopedModel):
    STATUS = [("pending", "در انتظار"), ("sent", "ارسال به صنعت و داور"),
              ("needs_fix", "نیازمند اصلاح"), ("paid", "تایید و پرداخت شد")]
    sabbatical = models.ForeignKey(Sabbatical, on_delete=models.CASCADE, related_name="reports")
    no = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    paid_amount = models.CharField(max_length=80, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "research_sabbatical_report"
        ordering = ["no"]
