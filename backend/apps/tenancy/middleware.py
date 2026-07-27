"""
Resolves the active tenant for each request and exposes it as `request.tenant`.

Priority: `X-Tenant` header (explicit workspace switch) → the JWT `tid` claim →
the authenticated user's home tenant. DRF authentication runs inside the view,
so we resolve lazily via a SimpleLazyObject that reads the (by-then populated)
`request.user` / `request.jwt_tenant_id`.
"""
from django.utils.functional import SimpleLazyObject


def _resolve_tenant(request):
    from .models import Tenant

    header_tid = request.META.get("HTTP_X_TENANT")
    if header_tid:
        tenant = Tenant.objects.filter(id=header_tid).first()
        if tenant:
            return tenant
    jwt_tid = getattr(request, "jwt_tenant_id", None)
    if jwt_tid:
        tenant = Tenant.objects.filter(id=jwt_tid).first()
        if tenant:
            return tenant
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return getattr(user, "tenant", None)
    return None


class CurrentTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = SimpleLazyObject(lambda: _resolve_tenant(request))
        return self.get_response(request)
