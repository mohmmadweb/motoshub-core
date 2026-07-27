from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import Contract, ContractApproval, Stage
from .serializers import ContractListSerializer, ContractSerializer


class ContractViewSet(TenantScopedModelViewSet):
    queryset = Contract.objects.select_related("owner").prefetch_related("payments", "approvals").all()
    required_perms = _crud_perms("contracts", extra={"advance": "contracts.stage", "approve": "contracts.stage"})
    filterset_fields = ["stage", "contract_type", "method"]
    search_fields = ["title", "vendor"]
    ordering_fields = ["created_at", "value", "deadline"]

    def get_serializer_class(self):
        return ContractListSerializer if self.action == "list" else ContractSerializer

    @action(detail=True, methods=["post"])
    def advance(self, request, pk=None):
        contract = self.get_object()
        order = [s.value for s in Stage]
        idx = order.index(contract.stage)
        if idx < len(order) - 1:
            contract.stage = order[idx + 1]
            contract.save(update_fields=["stage"])
        return Response({"stage": contract.stage})

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        contract = self.get_object()
        approval_id = (request.data or {}).get("approval_id")
        step = ContractApproval.objects.filter(id=approval_id, contract=contract).first()
        if not step:
            return Response({"error": {"code": 404, "type": "not_found", "message": "مرحلهٔ تأیید یافت نشد."}}, status=404)
        step.status = (request.data or {}).get("status", "approved")
        step.acted_at = timezone.now()
        step.save(update_fields=["status", "acted_at"])
        return Response({"id": str(step.id), "status": step.status})
