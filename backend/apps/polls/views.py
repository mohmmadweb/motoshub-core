from django.core.exceptions import ValidationError
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Poll, PollOption, PollVote
from .serializers import PollSerializer


class PollViewSet(TenantScopedModelViewSet):
    queryset = Poll.objects.select_related("author").prefetch_related("options__ballots").all()
    serializer_class = PollSerializer
    filterset_fields = ["group"]
    required_perms = {
        "list": "news.list", "retrieve": "news.list", "create": "news.create",
        "update": "news.edit", "partial_update": "news.edit", "destroy": "news.delete",
        "vote": "news.list",
    }

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        poll = self.get_object()
        try:
            option = PollOption.objects.filter(id=(request.data or {}).get("option_id"), poll=poll).first()
        except (ValueError, ValidationError):
            option = None  # malformed (non-UUID) option_id → treat as invalid, not a 500
        if not option:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "گزینه نامعتبر است."}}, status=422)
        PollVote.objects.update_or_create(poll=poll, user=request.user, defaults={"option": option, "tenant": request.tenant})
        # Count fresh from the DB (avoid the prefetched cache captured pre-vote).
        results = {str(row["id"]): row["n"] for row in poll.options.values("id").annotate(n=Count("ballots"))}
        return Response({"voted": str(option.id), "results": results})
