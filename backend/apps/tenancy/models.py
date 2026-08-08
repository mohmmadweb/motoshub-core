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

    # ── System identity and single sign-on ──────────────────────────────────
    # Where this installation's users come from. «بدون SSO» keeps local
    # accounts as the only source; anything else defers identity to the
    # organisation's own directory.
    SSO_PROVIDERS = [
        ("none", "بدون SSO"),
        ("ldap", "LDAP / Active Directory"),
        ("saml", "SAML 2.0"),
        ("oidc", "OpenID Connect"),
        ("otp", "ورود با موبایل (OTP)"),
    ]
    short_name = models.CharField(max_length=80, blank=True, help_text="نام کوتاه در رابط کاربری")
    sso_provider = models.CharField(max_length=8, choices=SSO_PROVIDERS, default="none")
    sso_url = models.CharField(max_length=300, blank=True, help_text="نشانی سرویس هویت")
    sso_auto_create = models.BooleanField(
        default=True, help_text="ایجاد خودکار حساب برای کاربرِ تاییدشده در منبع هویت"
    )
    # Kept on by default deliberately: turning it off with a misconfigured
    # directory would lock every administrator out of their own installation.
    sso_allow_local = models.BooleanField(
        default=True, help_text="اجازه‌ی ورود محلی در کنار SSO"
    )

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


class CompanyMembership(TimeStampedModel):
    """Which companies a user belongs to.

    A person can sit in more than one subsidiary — a shared services lead, an
    auditor covering several firms — so membership is a table rather than the
    single FK on User. That single FK stays as the user's home company; this is
    the full set their content scope is computed from.

    Membership is granted by a company's administrator. Users never choose it,
    which is the whole point: scope follows who you are, not what you pick.
    """
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="company_memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")

    class Meta(TimeStampedModel.Meta):
        db_table = "tenancy_company_membership"
        constraints = [
            models.UniqueConstraint(fields=["user", "company"], name="uniq_company_membership"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.company}"
