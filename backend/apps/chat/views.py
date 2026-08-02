from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Channel, Message
from .serializers import ChannelSerializer, MessageSerializer


class ChannelViewSet(TenantScopedModelViewSet):
    queryset = Channel.objects.select_related("owner").all()
    serializer_class = ChannelSerializer
    owner_field = "owner"
    required_perms = {
        "list": "chat.view", "retrieve": "chat.view", "create": "chat.channels",
        "update": "chat.channels", "partial_update": "chat.channels", "destroy": "chat.channels",
        "messages": "chat.view",
    }
    search_fields = ["name", "topic"]
    filterset_fields = ["channel_type", "category"]

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        channel = self.get_object()
        if request.method == "POST":
            text = (request.data or {}).get("text", "").strip()
            if not text:
                return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "متن پیام الزامی است."}}, status=422)
            msg = Message.objects.create(channel=channel, author=request.user, text=text, tenant=request.tenant)
            data = MessageSerializer(msg, context={"request": request}).data
            # Broadcast to any live WebSocket subscribers of this channel.
            layer = get_channel_layer()
            if layer is not None:
                async_to_sync(layer.group_send)(f"chat_{channel.id}", {"type": "chat.message", "message": data})
            return Response(data, status=201)
        qs = channel.messages.select_related("author").all()[:200]
        return Response(MessageSerializer(qs, many=True, context={"request": request}).data)


# ── Direct messages (1:1) ────────────────────────────────────────────────────
from django.db.models import Q  # noqa: E402
from rest_framework.permissions import IsAuthenticated  # noqa: E402
from rest_framework.views import APIView  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from .models import DirectMessage, Message, MessageReaction  # noqa: E402


class MessageReactView(APIView):
    """Toggle the current user's reaction (icon) on a channel message."""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id=None):
        msg = Message.objects.filter(id=message_id, tenant=request.tenant).select_related("channel").first()
        if not msg:
            return Response({"error": {"code": 404, "type": "not_found", "message": "پیام یافت نشد."}}, status=404)
        icon = (request.data or {}).get("icon")
        valid = {c[0] for c in MessageReaction.ICONS}
        if icon not in valid:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "واکنش نامعتبر است."}}, status=422)
        existing = MessageReaction.objects.filter(message=msg, user=request.user, icon=icon).first()
        if existing:
            existing.delete()
        else:
            MessageReaction.objects.create(tenant=request.tenant, message=msg, user=request.user, icon=icon)
        data = MessageSerializer(msg, context={"request": request}).data
        # Broadcast the updated reaction set to live channel subscribers.
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"chat_{msg.channel_id}", {"type": "chat.message", "message": data})
        return Response({"id": str(msg.id), "reactions": data["reactions"]})


class DmView(APIView):
    """GET → the current user's DM threads (grouped by peer, newest last).
    POST {to, text} → send a direct message. GET ?peer=<id> marks it read."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        me = request.user
        t = getattr(request, "tenant", None)
        qs = DirectMessage.objects.filter(tenant=t).filter(Q(sender=me) | Q(recipient=me)).select_related("sender", "recipient")
        threads = {}
        for m in qs:
            peer = m.recipient if m.sender_id == me.id else m.sender
            th = threads.setdefault(str(peer.id), {
                "id": str(peer.id), "with": peer.name, "avatarColor": peer.avatar_color,
                "online": peer.presence == "online", "messages": [], "unread": 0,
            })
            th["messages"].append({
                "id": str(m.id), "from": "me" if m.sender_id == me.id else "them",
                "text": m.text, "time": m.created_at.strftime("%H:%M"),
                "status": "read" if m.read else "delivered",
            })
            if m.recipient_id == me.id and not m.read:
                th["unread"] += 1
        out = []
        for th in threads.values():
            th["lastMessage"] = th["messages"][-1]["text"] if th["messages"] else ""
            th["time"] = th["messages"][-1]["time"] if th["messages"] else ""
            out.append(th)
        return Response(out)

    def post(self, request):
        me = request.user
        data = request.data or {}
        peer = User.objects.filter(id=data.get("to")).first()
        text = (data.get("text") or "").strip()
        if not peer or peer.id == me.id or not text:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "گیرنده یا متن نامعتبر است."}}, status=422)
        m = DirectMessage.objects.create(tenant=request.tenant, sender=me, recipient=peer, text=text)
        # Push to the recipient's live DM socket (from their perspective it's incoming).
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"dm_{peer.id}", {"type": "dm.message", "message": {
                "threadId": str(me.id), "with": me.name, "avatarColor": me.avatar_color,
                "id": str(m.id), "from": "them", "text": m.text, "time": m.created_at.strftime("%H:%M"),
            }})
        return Response({"id": str(m.id), "from": "me", "text": m.text, "time": m.created_at.strftime("%H:%M"), "status": "delivered"}, status=201)
