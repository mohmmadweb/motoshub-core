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

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None), is_system=False)

    def update(self, request, *args, **kwargs):
        if self.get_object().is_system:
            return Response({"error": {"code": 403, "type": "forbidden", "message": "نقش سیستمی قابل ویرایش نیست."}}, status=403)
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

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None))
