from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .catalog import (
    JURY_MAX,
    JURY_THRESHOLD,
    NF_STAGE_ORDER,
    SCREENING_MAX,
    SCREENING_THRESHOLD,
)
from .models import Fund, NfProject, NfRequest
from .serializers import FundSerializer, NfProjectListSerializer, NfProjectSerializer, NfRequestSerializer


class NfProjectViewSet(TenantScopedModelViewSet):
    queryset = NfProject.objects.select_related("fund_manager").prefetch_related(
        "guarantees", "reports__chain", "payments", "requests"
    ).all()
    owner_field = "fund_manager"
    required_perms = {
        "list": "funds.list", "retrieve": "funds.list",
        "create": "funds.submit", "update": "funds.monitor", "partial_update": "funds.monitor",
        "destroy": "funds.monitor", "advance": "funds.refer", "score": "funds.score",
        "request": "funds.monitor", "monitor": "funds.monitor",
    }
    filterset_fields = ["stage", "green_path", "field"]
    search_fields = ["code", "title_fa", "title_en", "rahbar"]
    ordering_fields = ["created_at", "budget", "progress"]

    def get_serializer_class(self):
        return NfProjectListSerializer if self.action == "list" else NfProjectSerializer

    @action(detail=True, methods=["post"])
    def advance(self, request, pk=None):
        """Move to the next stage — gated by the evaluation thresholds."""
        p = self.get_object()
        idx = NF_STAGE_ORDER.index(p.stage)
        # Gate: screening → jury needs screening pass; jury → approval needs jury pass.
        if p.stage == "screening" and (p.screening_score or 0) < SCREENING_THRESHOLD:
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": f"امتیاز غربالگری باید حداقل {SCREENING_THRESHOLD} از {SCREENING_MAX} باشد."}}, status=422)
        if p.stage == "jury" and (p.jury_score or 0) < JURY_THRESHOLD:
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": f"امتیاز داوری باید حداقل {JURY_THRESHOLD} از {JURY_MAX} باشد."}}, status=422)
        if idx < len(NF_STAGE_ORDER) - 1:
            p.stage = NF_STAGE_ORDER[idx + 1]
            p.save(update_fields=["stage"])
        return Response({"stage": p.stage})

    @action(detail=True, methods=["post"])
    def score(self, request, pk=None):
        p = self.get_object()
        data = request.data or {}
        if "screening_score" in data:
            p.screening_score = int(data["screening_score"])
        if "jury_score" in data:
            p.jury_score = int(data["jury_score"])
        p.save(update_fields=["screening_score", "jury_score"])
        return Response({
            "screening_score": p.screening_score, "screening_pass": (p.screening_score or 0) >= SCREENING_THRESHOLD,
            "jury_score": p.jury_score, "jury_pass": (p.jury_score or 0) >= JURY_THRESHOLD,
        })

    @action(detail=True, methods=["post"])
    def request(self, request, pk=None):
        """Log an out-of-contract request (extension / amendment / budget / letter)."""
        p = self.get_object()
        req = NfRequest.objects.create(
            tenant=request.tenant, project=p,
            request_type=(request.data or {}).get("request_type", "extend"),
            note=(request.data or {}).get("note", ""),
        )
        return Response(NfRequestSerializer(req).data, status=201)


class FundViewSet(TenantScopedModelViewSet):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    owner_field = None
    required_perms = {
        "list": "funds.list", "retrieve": "funds.list", "create": "funds.submit",
        "update": "funds.monitor", "partial_update": "funds.monitor", "destroy": "funds.monitor",
    }
    filterset_fields = ["stage"]
    search_fields = ["title", "applicant"]
