from django.core.exceptions import ValidationError
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Poll, PollOption, PollVote, Quiz, QuizAttempt
from .serializers import PollSerializer, QuizSerializer


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


class QuizViewSet(TenantScopedModelViewSet):
    queryset = Quiz.objects.select_related("author").prefetch_related("attempts").all()
    serializer_class = QuizSerializer
    owner_field = "author"
    filterset_fields = ["status"]
    search_fields = ["title"]
    # Uses only ids that exist in the 99-permission catalog. Whoever judges an
    # assessment («ارزیابی») owns its lifecycle, so edit and delete map there.
    required_perms = {
        "list": "training.list", "retrieve": "training.list", "create": "training.create",
        "update": "training.evaluate", "partial_update": "training.evaluate",
        "destroy": "training.evaluate", "submit": "training.enroll",
    }

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Record this user's score. Refuses once the assessment has closed, so
        a result cannot be filed after the deadline has passed."""
        quiz = self.get_object()
        if quiz.status == "closed":
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "این آزمون پایان یافته است."}}, status=422)
        try:
            score = int((request.data or {}).get("score", 0))
        except (TypeError, ValueError):
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "امتیاز نامعتبر است."}}, status=422)
        score = max(0, min(100, score))
        QuizAttempt.objects.update_or_create(
            quiz=quiz, user=request.user, defaults={"score": score, "tenant": request.tenant}
        )
        return Response({"score": score, "passed": score >= quiz.passing})
