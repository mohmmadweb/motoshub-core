from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Ticket, TicketMessage
from apps.notifications.services import notify

from .serializers import TicketMessageSerializer, TicketSerializer


class TicketViewSet(TenantScopedModelViewSet):
    queryset = Ticket.objects.select_related("author").prefetch_related("messages__author").all()
    serializer_class = TicketSerializer
    # Users see their own tickets; support/admins with tickets perms could see all.
    required_perms = {
        "list": "reports.view", "retrieve": "reports.view", "create": "reports.view",
        "update": "reports.view", "partial_update": "reports.view", "destroy": "reports.view",
        "reply": "reports.view", "close": "reports.view",
    }
    search_fields = ["subject", "number"]
    filterset_fields = ["status", "priority", "category"]

    def perform_create(self, serializer):
        import time
        number = f"TK-{int(time.time()) % 100000:05d}"
        body = serializer.validated_data.pop("body", "").strip()
        ticket = serializer.save(tenant=self.request.tenant, author=self.request.user, number=number)
        if body:
            TicketMessage.objects.create(
                ticket=ticket, author=self.request.user, body=body,
                from_support=False, tenant=self.request.tenant,
            )

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        body = (request.data or {}).get("body", "").strip()
        if not body:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "متن پیام الزامی است."}}, status=422)
        msg = TicketMessage.objects.create(ticket=ticket, author=request.user, body=body, tenant=request.tenant)
        ticket.status = "answered"
        ticket.save(update_fields=["status"])
        if ticket.author and ticket.author != request.user:
            notify(ticket.author, f"به تیکت «{ticket.subject}» پاسخ داده شد.", kind="comment", tenant=request.tenant)
        return Response(TicketMessageSerializer(msg, context={"request": request}).data, status=201)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = "closed"
        ticket.save(update_fields=["status"])
        return Response({"status": "closed"})
