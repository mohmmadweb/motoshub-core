from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import HasPerm

from .models import Company, Holding, Tenant
from .serializers import CompanySerializer, HoldingSerializer, TenantSerializer


class CurrentTenantView(APIView):
    """The active tenant (branding + enabled modules) for the signed-in user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return Response({"error": {"code": 404, "type": "not_found", "message": "سازمانی یافت نشد."}}, status=404)
        return Response(TenantSerializer(tenant).data)

    def patch(self, request):
        tenant = getattr(request, "tenant", None)
        user = request.user
        if not (user.is_superuser or "settings.branding" in user.get_permission_ids(tenant)):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicTenantsView(APIView):
    """Unauthenticated: the org list shown on the login screen."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response([
            {"id": str(t.id), "name": t.name, "domain": t.domain, "logo_color": t.logo_color}
            for t in Tenant.objects.all()[:50]
        ])


class PublicOrgStatsView(APIView):
    """Unauthenticated: the figures and holding names on the landing page.

    Aggregates and holding names only — nothing here identifies a person or
    exposes anything a visitor could not already read on the public site.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.accounts.models import User

        return Response({
            "holdings": [
                {"id": str(h.id), "name": h.name, "color": h.color}
                for h in Holding.objects.order_by("name")[:24]
            ],
            "holding_count": Holding.objects.count(),
            "company_count": Company.objects.count(),
            "user_count": User.objects.filter(is_active=True).count(),
        })


class _TenantScoped(ModelViewSet):
    permission_classes = [HasPerm]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return super().get_queryset().filter(tenant=tenant) if tenant else super().get_queryset().none()

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None))


class HoldingViewSet(_TenantScoped):
    queryset = Holding.objects.prefetch_related("companies").all()
    serializer_class = HoldingSerializer
    required_perms = {
        "list": "companies.view", "retrieve": "companies.view", "create": "companies.manage",
        "update": "companies.manage", "partial_update": "companies.manage", "destroy": "companies.manage",
    }
    search_fields = ["name"]


class CompanyViewSet(_TenantScoped):
    queryset = Company.objects.select_related("holding").all()
    serializer_class = CompanySerializer
    required_perms = HoldingViewSet.required_perms
    filterset_fields = ["holding"]
    search_fields = ["name"]


class MyScopeView(APIView):
    """GET → everything the caller needs to render their own reach.

    One request answers three questions the interface keeps asking: what level
    am I at, which domains may I switch between, and what may I publish. The
    same values are enforced server-side, so this is describing a decision
    already made rather than making one.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.rbac.models import RoleAssignment

        from .scope import scope_for

        tenant = getattr(request, "tenant", None)
        holdings = list(Holding.objects.filter(tenant=tenant).order_by("name"))
        companies = list(Company.objects.filter(tenant=tenant).order_by("name"))
        session = scope_for(request.user, tenant)

        assignment = (
            RoleAssignment.objects.filter(user=request.user)
            .select_related("role").order_by("-role__scope").first()
        )
        role = assignment.role if assignment else None

        return Response({
            **session.as_dict(holdings, companies),
            "role": {
                "id": str(role.id) if role else "",
                "title": role.title if role else "عضو عادی",
                "scope": role.scope if role else "tenant",
                "permissions": sorted(request.user.get_permission_ids(tenant)),
            },
            "holdings": [
                {"id": str(h.id), "name": h.name, "color": h.color,
                 "companies": [{"id": str(c.id), "name": c.name}
                               for c in companies if c.holding_id == h.id]}
                for h in holdings
            ],
            "companies": [
                {"id": str(c.id), "name": c.name, "holdingId": str(c.holding_id)}
                for c in companies
            ],
        })
