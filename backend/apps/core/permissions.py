"""
RBAC permission gate.

Usage on a ViewSet:

    class NewsViewSet(ModelViewSet):
        permission_classes = [HasPerm]
        required_perms = {
            "list": "news.list", "retrieve": "news.list",
            "create": "news.create", "update": "news.edit",
            "partial_update": "news.edit", "destroy": "news.delete",
        }

The user's effective permission-id set is resolved (and cached) by the rbac app
from their role assignments within the active tenant.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


def maintenance_blocks(request) -> bool:
    """True when «حالت تعمیر و نگهداری» is on and this caller is not exempt.

    Checked here rather than in middleware: the tenant is resolved from the JWT
    by DRF's authentication, which runs *after* middleware, so a middleware
    would see an unresolved tenant on every request.

    Reads stay open so the platform degrades to read-only rather than going
    dark; writes are refused for everyone except holders of settings.system,
    who need access to switch it back off.
    """
    if request.method in SAFE_METHODS:
        return False
    tenant = getattr(request, "tenant", None)
    if tenant is None or getattr(tenant, "pk", None) is None:
        return False
    from apps.console.models import WorkflowSettings
    on = (
        WorkflowSettings.objects.filter(tenant=tenant)
        .values_list("maintenance_mode", flat=True)
        .first()
    )
    if not on:
        return False
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return True
    if getattr(user, "is_superuser", False):
        return False
    return "settings.system" not in user.get_permission_ids(tenant)


class HasPerm(BasePermission):
    message = "برای این عملیات مجوز لازم را ندارید."

    def has_permission(self, request, view):
        if maintenance_blocks(request):
            self.message = "سامانه در حال به‌روزرسانی است؛ لطفاً بعداً تلاش کنید."
            return False
        required = getattr(view, "required_perms", {})
        # A view with no map is treated as authenticated-only.
        perm = required.get(view.action) if hasattr(view, "action") else None
        if perm is None:
            return bool(request.user and request.user.is_authenticated)
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_superuser", False):
            return True
        return perm in user.get_permission_ids(request.tenant)
