from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet, CurrentTenantView, HoldingViewSet, MyScopeView,
    PublicOrgStatsView, PublicTenantsView,
)

router = DefaultRouter(trailing_slash=False)
router.register("holdings", HoldingViewSet, basename="holding")
router.register("companies", CompanyViewSet, basename="company")

urlpatterns = router.urls + [
    path("tenant", CurrentTenantView.as_view(), name="current-tenant"),
    path("my/scope", MyScopeView.as_view(), name="my-scope"),
    path("public/tenants", PublicTenantsView.as_view(), name="public-tenants"),
    path("public/org-stats", PublicOrgStatsView.as_view(), name="public-org-stats"),
]
