from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ListModelMixin, GenericViewSet):
    """A user sees only their OWN notifications (no cross-user leakage)."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["read", "kind"]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return Notification.objects.filter(user=self.request.user, tenant=tenant)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        return Response({"count": self.get_queryset().filter(read=False).count()})

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        n = self.get_object(); n.read = True; n.save(update_fields=["read"])
        return Response({"read": True})

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        n = self.get_queryset().filter(read=False).update(read=True)
        return Response({"marked": n})
