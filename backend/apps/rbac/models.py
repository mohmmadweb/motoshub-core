"""
RBAC: Role (a named permission-id set with a scope) + RoleAssignment
(user ↔ role within a tenant, optionally narrowed to a holding/company/group).

Permission ids are validated against the in-code catalog, so the catalog stays
the single source of truth while roles remain fully CRUD-able per tenant.
"""
from django.db import models

from apps.core.models import TimeStampedModel


class RoleScope(models.TextChoices):
    PLATFORM = "platform", "پلتفرم"
    TENANT = "tenant", "سازمان"
    GROUP = "group", "گروه"


class Role(TimeStampedModel):
    # Preset roles are global (tenant is null); custom roles belong to a tenant.
    tenant = models.ForeignKey(
        "tenancy.Tenant", on_delete=models.CASCADE, related_name="roles", null=True, blank=True
    )
    key = models.SlugField(max_length=64, blank=True, help_text="کلید یکتا برای نقش‌های سیستمی")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=12, choices=RoleScope.choices, default=RoleScope.TENANT)
    permissions = models.JSONField(default=list, help_text="فهرست شناسه‌های مجوز")
    is_system = models.BooleanField(default=False, help_text="نقش پیش‌فرض غیرقابل‌حذف")

    class Meta(TimeStampedModel.Meta):
        db_table = "rbac_role"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "title"], name="uniq_role_title_per_tenant"),
        ]

    def __str__(self):
        return self.title


class RoleAssignment(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    tenant = models.ForeignKey(
        "tenancy.Tenant", on_delete=models.CASCADE, related_name="role_assignments", null=True, blank=True
    )
    # Optional narrowing of a group/company-scoped role.
    holding = models.ForeignKey("tenancy.Holding", on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey("tenancy.Company", on_delete=models.CASCADE, null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "rbac_role_assignment"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role", "tenant"], name="uniq_user_role_tenant"
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.role}"
