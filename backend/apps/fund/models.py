"""
Innovation Fund (صندوق نوآور) — the richest aggregate.

An NfProject is a dossier with a two-level state machine (stage × sub_status),
evaluation gates (screening 200 / jury 100), and child collections: guarantees,
reports (+ approval chain), payments, and out-of-contract requests.
"""
from django.db import models

from apps.core.models import TenantScopedModel
from .catalog import NF_STAGES


class NfProject(TenantScopedModel):
    code = models.CharField(max_length=32, help_text="کد طرح، مثل NF-1405-0001")
    title_fa = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300, blank=True)
    field = models.CharField(max_length=200, blank=True)
    macro_field = models.CharField(max_length=200, blank=True)

    rahbar = models.CharField(max_length=200, blank=True, help_text="شرکت شتابدهنده/راهبر")
    nazer = models.CharField(max_length=200, blank=True, help_text="ناظر")
    fund_manager = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="managed_nf")

    budget = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    share_percent = models.PositiveSmallIntegerField(default=0, help_text="سهم صندوق (٪)")
    duration_months = models.PositiveSmallIntegerField(default=0)
    contract_no = models.CharField(max_length=64, blank=True)

    stage = models.CharField(max_length=12, choices=NF_STAGES, default="proposal")
    sub_status = models.CharField(max_length=200, blank=True)
    green_path = models.BooleanField(default=False, help_text="مسیر سبز/تسریع")
    progress = models.PositiveSmallIntegerField(default=0)

    # Evaluation gates.
    screening_score = models.PositiveSmallIntegerField(null=True, blank=True)
    jury_score = models.PositiveSmallIntegerField(null=True, blank=True)

    # Team snapshot.
    team_name = models.CharField(max_length=200, blank=True)
    team_type = models.CharField(max_length=60, blank=True)
    team_city = models.CharField(max_length=120, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_project"
        constraints = [models.UniqueConstraint(fields=["tenant", "code"], name="uniq_nf_code_per_tenant")]

    def __str__(self):
        return f"{self.code} — {self.title_fa}"


class NfGuarantee(TenantScopedModel):
    project = models.ForeignKey(NfProject, on_delete=models.CASCADE, related_name="guarantees")
    kind = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    status = models.CharField(max_length=20, default="pending")  # received/pending/released

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_guarantee"


class NfReport(TenantScopedModel):
    REPORT_STATUS = [
        ("pending_upload", "در انتظار بارگذاری"),
        ("under_review", "در حال بررسی"),
        ("needs_fix", "نیازمند اصلاح"),
        ("approved", "تایید نهایی"),
    ]
    project = models.ForeignKey(NfProject, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=40, default="stage")  # stage/monthly/interactions/final
    title = models.CharField(max_length=200)
    due = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=REPORT_STATUS, default="pending_upload")

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_report"


class NfReportChainStep(TenantScopedModel):
    report = models.ForeignKey(NfReport, on_delete=models.CASCADE, related_name="chain")
    role = models.CharField(max_length=60)  # fund_manager/rahbar/nazer
    name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="pending")  # approved/pending/needs_fix
    late = models.BooleanField(default=False, help_text="تشدید ۱۵ روزه")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_report_chain"
        ordering = ["order"]


class NfPayment(TenantScopedModel):
    PAYMENT_STATUS = [
        ("await_order", "در انتظار دستور پرداخت"),
        ("ordered", "دستور پرداخت صادر شد"),
        ("paid", "پرداخت انجام شد"),
        ("docs_to_fund", "اسناد تحویل صندوق شد"),
        ("docs_to_team", "اسناد به تیم مجری ارسال شد"),
    ]
    project = models.ForeignKey(NfProject, on_delete=models.CASCADE, related_name="payments")
    payment_type = models.CharField(max_length=40, default="stage")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    status = models.CharField(max_length=16, choices=PAYMENT_STATUS, default="await_order")
    doc_no = models.CharField(max_length=64, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_payment"


class NfRequest(TenantScopedModel):
    project = models.ForeignKey(NfProject, on_delete=models.CASCADE, related_name="requests")
    request_type = models.CharField(max_length=60)  # extend/amendment/budget/letter
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="pending")  # pending/approved/rejected

    class Meta(TenantScopedModel.Meta):
        db_table = "fund_nf_request"
