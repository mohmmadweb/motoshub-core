from django.db.models import F
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Challenge, ChallengeMembership, Competition, CompetitionEntry, EntryVote
from .serializers import ChallengeSerializer, CompetitionSerializer, EntrySerializer


class CompetitionViewSet(TenantScopedModelViewSet):
    queryset = Competition.objects.prefetch_related("entries__votes").all()
    serializer_class = CompetitionSerializer
    owner_field = None
    filterset_fields = ["status", "category"]
    search_fields = ["title", "category"]

    @action(detail=False, methods=["post"])
    def vote(self, request):
        """Toggle the current user's vote on an entry (?entry=<id>)."""
        entry_id = request.query_params.get("entry") or (request.data or {}).get("entry")
        entry = CompetitionEntry.objects.filter(id=entry_id, tenant=request.tenant).first()
        if not entry:
            return Response({"error": {"code": 404, "type": "not_found", "message": "اثر یافت نشد."}}, status=404)
        existing = EntryVote.objects.filter(entry=entry, user=request.user).first()
        if existing:
            existing.delete()
            my_vote = False
        else:
            EntryVote.objects.create(tenant=request.tenant, entry=entry, user=request.user)
            my_vote = True
        return Response({"votes": EntryVote.objects.filter(entry=entry).count(), "my_vote": my_vote})


class CompetitionEntryViewSet(TenantScopedModelViewSet):
    """Submitting and withdrawing a work — «ارسال اثر» in the competition card.

    Entries are read through the nested list on the competition; this ViewSet
    exists for the write side, which the competition serializer treats as
    read-only.
    """
    queryset = CompetitionEntry.objects.select_related("competition").prefetch_related("votes").all()
    serializer_class = EntrySerializer
    owner_field = None
    filterset_fields = ["competition"]

    # Rotates through the same palette the prototype used, so a fresh entry
    # lands on a different swatch than the one before it.
    PALETTE = ["#5e7191", "#0d9488", "#b45309", "#1f4f99", "#7c3aed"]

    def perform_create(self, serializer):
        competition = serializer.validated_data["competition"]
        entry = serializer.save(
            tenant=getattr(self.request, "tenant", None),
            by=self.request.user.name or self.request.user.username,
            color=self.PALETTE[competition.entries.count() % len(self.PALETTE)],
        )
        Competition.objects.filter(pk=competition.pk).update(participants=F("participants") + 1)
        return entry

    def perform_destroy(self, instance):
        competition_id = instance.competition_id
        instance.delete()
        # Never let the counter fall below zero if it was seeded lower than the
        # number of entries.
        Competition.objects.filter(pk=competition_id, participants__gt=0).update(participants=F("participants") - 1)


class ChallengeViewSet(TenantScopedModelViewSet):
    queryset = Challenge.objects.prefetch_related("members").all()
    serializer_class = ChallengeSerializer
    owner_field = None
    filterset_fields = ["kind", "status", "category"]
    search_fields = ["title", "category"]

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        """Toggle the current user's membership in this challenge."""
        challenge = self.get_object()
        existing = ChallengeMembership.objects.filter(challenge=challenge, user=request.user).first()
        if existing:
            existing.delete()
            is_joined = False
        else:
            ChallengeMembership.objects.create(tenant=request.tenant, challenge=challenge, user=request.user)
            is_joined = True
        return Response({"joined": ChallengeMembership.objects.filter(challenge=challenge).count(), "is_joined": is_joined})
