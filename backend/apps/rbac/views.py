from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from apps.core.permissions import HasPerm

from .catalog import PERMISSION_CATALOG
from .models import Role, RoleAssignment
from .serializers import RoleAssignmentSerializer, RoleSerializer


class RoleViewSet(ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "list": "roles.list", "retrieve": "roles.list", "create": "roles.create",
        "update": "roles.edit", "partial_update": "roles.edit", "destroy": "roles.delete",
    }

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        # System (global) roles + this tenant's custom roles.
        return Role.objects.filter(Q(tenant__isnull=True) | Q(tenant=tenant))

    def _excess(self, request) -> list[str]:
        """Permissions being granted that the caller does not hold themselves.

        Without this check, anyone with roles.create could mint a role carrying
        every permission in the catalog — including settings.system — and
        assign it to themselves. Delegation must never be able to manufacture
        authority its author lacks.
        """
        wanted = set((request.data or {}).get("permissions") or [])
        if not wanted or request.user.is_superuser:
            return []
        mine = request.user.get_permission_ids(getattr(request, "tenant", None))
        return sorted(wanted - set(mine))

    def create(self, request, *args, **kwargs):
        excess = self._excess(request)
        if excess:
            return Response({"error": {"code": 403, "type": "forbidden", "message":
                f"نمی‌توانید دسترسی‌هایی را بدهید که خودتان ندارید: {'، '.join(excess[:5])}"}}, status=403)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None), is_system=False)

    def update(self, request, *args, **kwargs):
        if self.get_object().is_system:
            return Response({"error": {"code": 403, "type": "forbidden", "message": "نقش سیستمی قابل ویرایش نیست."}}, status=403)
        excess = self._excess(request)
        if excess:
            return Response({"error": {"code": 403, "type": "forbidden", "message":
                f"نمی‌توانید دسترسی‌هایی را بدهید که خودتان ندارید: {'، '.join(excess[:5])}"}}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().is_system:
            return Response({"error": {"code": 403, "type": "forbidden", "message": "نقش سیستمی قابل حذف نیست."}}, status=403)
        return super().destroy(request, *args, **kwargs)


class PermissionCatalogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([
            {"group": g, "label": label, "permissions": [{"id": f"{g}.{a}", "action": a} for a in actions]}
            for g, label, actions in PERMISSION_CATALOG
        ])


class AssignmentViewSet(ModelViewSet):
    serializer_class = RoleAssignmentSerializer
    permission_classes = [HasPerm]
    required_perms = {"create": "roles.assign", "destroy": "roles.assign", "list": "roles.list"}
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return RoleAssignment.objects.filter(tenant=tenant)

    def create(self, request, *args, **kwargs):
        """Assigning a role must not hand out more than the assigner holds.

        The same escalation as building an over-powered role, reached from the
        other direction: granting someone an existing role that outranks you.
        """
        role = Role.objects.filter(id=(request.data or {}).get("role")).first()
        if role and not request.user.is_superuser:
            mine = set(request.user.get_permission_ids(getattr(request, "tenant", None)))
            excess = sorted(set(role.permissions or []) - mine)
            if excess:
                return Response({"error": {"code": 403, "type": "forbidden", "message":
                    f"این نقش دسترسی‌هایی دارد که خودتان ندارید: {'، '.join(excess[:5])}"}}, status=403)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None))
