"""
Tenancy: the isolation hierarchy.

    Tenant  (customer org / billing + isolation boundary, e.g. «بنیاد مستضعفان»)
      └── Holding   (internal grouping, e.g. «هلدینگ صنایع غذایی سینا»)
            └── Company   (sub-company, e.g. «بهنوش ایران»)

Holdings/Companies are optional (a small tenant may have neither) and fully
CRUD-able. Content is scoped by (tenant) + optionally (holding|company) via the
ContentScope axis on scoped content.
"""
from django.db import models

from apps.core.models import TimeStampedModel


class Plan(models.TextChoices):
    BASIC = "basic", "پایه"
    PRO = "pro", "حرفه‌ای"
    ENTERPRISE = "enterprise", "سازمانی"


class Tenant(TimeStampedModel):
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, unique=True)
    logo_color = models.CharField(max_length=9, default="#1f4f99")
    plan = models.CharField(max_length=12, choices=Plan.choices, default=Plan.ENTERPRISE)
    enabled_modules = models.JSONField(default=list, blank=True)
    cross_tenant = models.BooleanField(default=False, help_text="تعامل بین‌سازمانی")

    class Meta(TimeStampedModel.Meta):
        db_table = "tenancy_tenant"

    def __str__(self):
        return self.name


class Holding(TimeStampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="holdings")
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=9, default="#0d9488")

    class Meta(TimeStampedModel.Meta):
        db_table = "tenancy_holding"

    def __str__(self):
        return self.name


class Company(TimeStampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="companies")
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, related_name="companies")
    name = models.CharField(max_length=200)

    class Meta(TimeStampedModel.Meta):
        db_table = "tenancy_company"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name
