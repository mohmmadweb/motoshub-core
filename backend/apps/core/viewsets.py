"""
Shared ViewSet base for tenant-scoped domain resources.

Filters every queryset to `request.tenant`, stamps `tenant` (and `author`/`owner`
when present) on create, and gates each action through `HasPerm` using the
`required_perms` map declared on the subclass.
"""
from rest_framework.viewsets import ModelViewSet

from .permissions import HasPerm


class TenantScopedModelViewSet(ModelViewSet):
    permission_classes = [HasPerm]
    required_perms: dict = {}
    # Field on the model to stamp with request.user on create, if any.
    owner_field: str | None = "author"

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            return qs.filter(tenant=tenant)
        return qs.none()

    def perform_create(self, serializer):
        extra = {"tenant": getattr(self.request, "tenant", None)}
        if self.owner_field and self.owner_field in {f.name for f in serializer.Meta.model._meta.get_fields()}:
            extra[self.owner_field] = self.request.user
        serializer.save(**extra)
