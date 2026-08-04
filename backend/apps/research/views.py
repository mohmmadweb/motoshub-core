from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import ResearchOpportunity, RfpCall, Sabbatical
from .serializers import ResearchOpportunitySerializer, RfpCallSerializer, SabbaticalSerializer


class ResearchViewSet(TenantScopedModelViewSet):
    queryset = ResearchOpportunity.objects.prefetch_related("applications").all()
    serializer_class = ResearchOpportunitySerializer
    required_perms = _crud_perms("research", extra={"update": "research.edit", "destroy": "research.close"})
    filterset_fields = ["stage", "field"]
    search_fields = ["title", "field", "supervisor"]


class RfpCallViewSet(TenantScopedModelViewSet):
    queryset = RfpCall.objects.prefetch_related("vendors").all()
    serializer_class = RfpCallSerializer
    owner_field = None
    required_perms = {"list": "research.list", "retrieve": "research.list", "create": "research.create",
                      "update": "research.edit", "partial_update": "research.edit", "destroy": "research.close"}
    filterset_fields = ["stage", "holding"]
    search_fields = ["title", "company", "holding"]


class SabbaticalViewSet(TenantScopedModelViewSet):
    queryset = Sabbatical.objects.prefetch_related("reports").all()
    serializer_class = SabbaticalSerializer
    owner_field = None
    required_perms = RfpCallViewSet.required_perms
    filterset_fields = ["stage"]
    search_fields = ["professor", "university", "industry", "topic"]
