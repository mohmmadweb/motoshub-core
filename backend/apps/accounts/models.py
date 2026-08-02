"""Accounts: custom user + presence. Users belong to a tenant (their home org)."""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.cache import cache
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra):
        if not username:
            raise ValueError("username الزامی است")
        user = self.model(username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra)


class PresenceStatus(models.TextChoices):
    ONLINE = "online", "آنلاین"
    AWAY = "away", "غایب"
    DND = "dnd", "مزاحم نشوید"
    OFFLINE = "offline", "آفلاین"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, help_text="سمت/نقش نمایشی")
    org = models.CharField(max_length=200, blank=True, help_text="سازمان/شرکت نمایشی")
    avatar_color = models.CharField(max_length=9, default="#1f4f99")
    skills = models.JSONField(default=list, blank=True)
    presence = models.CharField(max_length=8, choices=PresenceStatus.choices, default=PresenceStatus.OFFLINE)

    # Home tenant + the company/holding the user belongs to (content scoping).
    tenant = models.ForeignKey(
        "tenancy.Tenant", on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )
    company = models.ForeignKey(
        "tenancy.Company", on_delete=models.SET_NULL, related_name="members", null=True, blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "accounts_user"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.name or self.username

    # ── RBAC bridge ─────────────────────────────────────────────────────────
    def get_permission_ids(self, tenant=None) -> set[str]:
        """Effective permission-id set within a tenant (cached 5 min)."""
        tenant_id = getattr(tenant, "id", tenant) or self.tenant_id
        cache_key = f"perms:{self.id}:{tenant_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        from apps.rbac.models import RoleAssignment

        perms: set[str] = set()
        qs = RoleAssignment.objects.filter(user=self).select_related("role")
        if tenant_id:
            qs = qs.filter(models.Q(tenant_id=tenant_id) | models.Q(tenant__isnull=True))
        for assignment in qs:
            perms.update(assignment.role.permissions or [])
        cache.set(cache_key, perms, 300)
        return perms
