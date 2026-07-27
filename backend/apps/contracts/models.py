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
