from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import AwardEntry, AwardTrack
from .serializers import AwardEntrySerializer, AwardTrackSerializer


class AwardTrackViewSet(TenantScopedModelViewSet):
    queryset = AwardTrack.objects.prefetch_related("entries").all()
    serializer_class = AwardTrackSerializer
    owner_field = None
    required_perms = {"list": "award.list", "retrieve": "award.list", "create": "award.judge",
                      "update": "award.judge", "partial_update": "award.judge", "destroy": "award.judge"}
    search_fields = ["title"]


class AwardEntryViewSet(TenantScopedModelViewSet):
    queryset = AwardEntry.objects.select_related("track").all()
    serializer_class = AwardEntrySerializer
    owner_field = None
    required_perms = {"list": "award.list", "retrieve": "award.list", "create": "award.list",
                      "update": "award.list", "partial_update": "award.list", "destroy": "award.judge",
                      "validate": "award.validate", "judge": "award.score"}
    filterset_fields = ["track", "status"]

    def update(self, request, *args, **kwargs):
        # Enforce the one-time-edit rule from the prototype.
        entry = self.get_object()
        if entry.edit_used:
            return Response({"error": {"code": 403, "type": "forbidden", "message": "امکان ویرایش فقط یک‌بار وجود دارد."}}, status=403)
        resp = super().update(request, *args, **kwargs)
        entry.refresh_from_db(); entry.edit_used = True; entry.save(update_fields=["edit_used"])
        return resp

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        e = self.get_object(); e.status = "judging"; e.save(update_fields=["status"])
        return Response({"status": e.status})

    @action(detail=True, methods=["post"])
    def judge(self, request, pk=None):
        e = self.get_object()
        e.score = int((request.data or {}).get("score", 0)); e.status = "scored"
        e.save(update_fields=["score", "status"])
        return Response({"score": e.score, "status": e.status})
