"""Contracts: record with a stage machine, payment schedule, and approval chain."""
from django.db import models

from apps.core.models import TenantScopedModel


class Stage(models.TextChoices):
    NEGOTIATION = "negotiation", "مذاکره"
    RFP = "rfp", "فراخوان"
    EVALUATION = "evaluation", "داوری"
    EXECUTING = "executing", "در حال اجرا"
    SETTLED = "settled", "تسویه‌شده"


class ContractType(models.TextChoices):
    TECH = "tech", "فناورانه"
    RESEARCH = "research", "پژوهشی"
    CONSTRUCTION = "construction", "عمرانی"
    SERVICE = "service", "خدماتی"


class Method(models.TextChoices):
    PUBLIC_CALL = "public_call", "فراخوان عمومی"
    LIMITED = "limited", "استعلام محدود"
    NO_TENDER = "no_tender", "ترک تشریفات"


class Contract(TenantScopedModel):
    title = models.CharField(max_length=300)
    vendor = models.CharField(max_length=200, blank=True)
    stage = models.CharField(max_length=12, choices=Stage.choices, default=Stage.NEGOTIATION)
    contract_type = models.CharField(max_length=14, choices=ContractType.choices, default=ContractType.SERVICE)
    method = models.CharField(max_length=12, choices=Method.choices, default=Method.PUBLIC_CALL)
    value = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    guarantee = models.CharField(max_length=120, blank=True)
    deadline = models.DateField(null=True, blank=True)
    owner = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="contracts")

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_contract"

    def __str__(self):
        return self.title


class PaymentStatus(models.TextChoices):
    PAID = "paid", "پرداخت‌شده"
    PENDING = "pending", "در انتظار تأیید"
    FUTURE = "future", "آینده"


class ContractPayment(TenantScopedModel):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="payments")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    due = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=PaymentStatus.choices, default=PaymentStatus.FUTURE)

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_payment"
        ordering = ["due"]


class ApprovalStatus(models.TextChoices):
    APPROVED = "approved", "تأیید شده"
    PENDING = "pending", "در انتظار"
    REJECTED = "rejected", "رد شده"


class ContractApproval(TenantScopedModel):
    """One step of the signature/approval chain."""

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="approvals")
    role = models.CharField(max_length=120)
    name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=8, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    order = models.PositiveSmallIntegerField(default=0)
    acted_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_approval"
        ordering = ["order"]


# ── Rich Daneshmand sub-modules (portfolio views under the Contracts page) ────
class TechTransferContract(TenantScopedModel):
    """Technology-transfer portfolio row (متن آزاد + سه محور پیشرفت)."""
    kind = models.CharField(max_length=60, default="تبادل فناوری", help_text="نوع قرارداد")
    title = models.CharField(max_length=300)
    nazer = models.CharField(max_length=200, blank=True, help_text="ناظر فنی پروژه")
    city = models.CharField(max_length=120, blank=True)
    holding = models.CharField(max_length=200, blank=True, help_text="هلدینگ متقاضی")
    company = models.CharField(max_length=200, blank=True, help_text="شرکت متقاضی")
    mojri = models.CharField(max_length=200, blank=True, help_text="مجری پروژه")
    company_role = models.CharField(max_length=120, blank=True)
    daneshmand_role = models.CharField(max_length=120, blank=True)
    amount = models.CharField(max_length=80, blank=True, help_text="مبلغ قرارداد (نمایشی)")
    commitment = models.CharField(max_length=80, blank=True, help_text="تعهد بنیاد (نمایشی)")
    physical_progress = models.PositiveSmallIntegerField(default=0)
    time_progress = models.PositiveSmallIntegerField(default=0)
    financial_progress = models.PositiveSmallIntegerField(default=0)
    guarantee = models.CharField(max_length=120, blank=True)
    note = models.CharField(max_length=300, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_tech_transfer"

    def __str__(self):
        return self.title


class Tender(TenantScopedModel):
    """مناقصه/مزایده — کمیسیون معاملات."""
    METHODS = [("public", "مناقصه عمومی"), ("limited", "مناقصه محدود"),
               ("auction", "مزایده"), ("no_formality", "ترک تشریفات")]
    STAGES = [("publish", "انتشار آگهی"), ("receive", "دریافت پاکات"),
              ("commission", "کمیسیون معاملات"), ("award", "ابلاغ برنده"), ("contract", "عقد قرارداد")]
    title = models.CharField(max_length=300)
    method = models.CharField(max_length=14, choices=METHODS, default="public")
    stage = models.CharField(max_length=12, choices=STAGES, default="publish")
    participants = models.PositiveSmallIntegerField(default=0)
    session_date = models.CharField(max_length=20, blank=True, help_text="تاریخ جلسه (جلالی نمایشی)")
    winner = models.CharField(max_length=200, blank=True)
    note = models.CharField(max_length=300, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_tender"

    def __str__(self):
        return self.title


class ESignDocument(TenantScopedModel):
    """گردش امضای الکترونیک — سند + زنجیرهٔ امضا."""
    KINDS = [("nf", "قرارداد صندوق نوآور"), ("tech", "قرارداد تبادل فناوری"),
             ("amendment", "متمم قرارداد"), ("minutes", "صورت‌جلسه")]
    title = models.CharField(max_length=400)
    kind = models.CharField(max_length=12, choices=KINDS, default="nf")
    related_to = models.CharField(max_length=120, blank=True)
    method = models.CharField(max_length=60, default="امضای الکترونیک غیرحضوری")
    letter_no = models.CharField(max_length=64, blank=True, help_text="شماره نامه پس از تکمیل امضاها")

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_esign_doc"

    def __str__(self):
        return self.title


class ESignStep(TenantScopedModel):
    STATUS = [("signed", "امضا شد"), ("awaiting", "در انتظار امضا"), ("queued", "در نوبت")]
    document = models.ForeignKey(ESignDocument, on_delete=models.CASCADE, related_name="steps")
    role = models.CharField(max_length=120)
    name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="queued")
    date = models.CharField(max_length=20, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "contracts_esign_step"
        ordering = ["order"]
