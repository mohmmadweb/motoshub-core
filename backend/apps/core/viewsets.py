"""
Shared ViewSet base for tenant-scoped domain resources.

Filters every queryset to `request.tenant`, narrows it further to the caller's
organisational scope when the model carries one, stamps `tenant` (and
`author`/`owner` when present) on create, and gates each action through
`HasPerm` using the `required_perms` map declared on the subclass.
"""
from rest_framework.viewsets import ModelViewSet

from .permissions import HasPerm


class TenantScopedModelViewSet(ModelViewSet):
    permission_classes = [HasPerm]
    required_perms: dict = {}
    # Field on the model to stamp with request.user on create, if any.
    owner_field: str | None = "author"

    def _model_is_scoped(self) -> bool:
        """Whether this model participates in holding/company scoping."""
        fields = {f.name for f in self.queryset.model._meta.get_fields()}
        return {"scope", "holding", "company"} <= fields

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return qs.none()
        qs = qs.filter(tenant=tenant)

        # Organisational scope, enforced here rather than only in the UI: a
        # subsidiary's content must not reach another subsidiary even when the
        # request is crafted by hand. Models without the scope columns are
        # unaffected.
        if not self._model_is_scoped():
            return qs

        from apps.tenancy.scope import scope_for

        session = scope_for(self.request.user, tenant)
        # The caller may look at a narrower domain than they belong to; the
        # headers can only narrow, never widen, because visible_q is built from
        # the session's own memberships.
        active_holding = self.request.headers.get("X-Scope-Holding") or None
        active_company = self.request.headers.get("X-Scope-Company") or None
        if active_company and str(active_company) not in {str(c) for c in session.company_ids} \
                and session.level != "سیستم":
            active_company = None
        if active_holding and str(active_holding) not in {str(h) for h in session.holding_ids} \
                and session.level != "سیستم":
            active_holding = None

        condition = session.visible_q(active_holding, active_company)
        return qs if condition is None else qs.filter(condition)

    def perform_create(self, serializer):
        extra = {"tenant": getattr(self.request, "tenant", None)}
        if self.owner_field and self.owner_field in {f.name for f in serializer.Meta.model._meta.get_fields()}:
            extra[self.owner_field] = self.request.user
        serializer.save(**extra)
