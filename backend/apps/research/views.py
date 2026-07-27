from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import ResearchOpportunity
from .serializers import ResearchOpportunitySerializer


class ResearchViewSet(TenantScopedModelViewSet):
    queryset = ResearchOpportunity.objects.prefetch_related("applications").all()
    serializer_class = ResearchOpportunitySerializer
    required_perms = _crud_perms("research", extra={"update": "research.edit", "destroy": "research.close"})
    filterset_fields = ["stage", "field"]
    search_fields = ["title", "field", "supervisor"]
