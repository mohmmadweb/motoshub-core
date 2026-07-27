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
from rest_framework.permissions import BasePermission


class HasPerm(BasePermission):
    message = "برای این عملیات مجوز لازم را ندارید."

    def has_permission(self, request, view):
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
