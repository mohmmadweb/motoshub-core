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
            data = request.data or {}
            text = data.get("text", "").strip()
            if not text:
                return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "متن پیام الزامی است."}}, status=422)
            # A reply keeps its parent, which is what makes a thread a thread.
            parent = None
            if data.get("reply_to_id"):
                parent = Message.objects.filter(id=data["reply_to_id"], channel=channel).first()
            msg = Message.objects.create(
                channel=channel, author=request.user, text=text,
                reply_to=parent, tenant=request.tenant,
            )
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
from .models import Call, DirectMessage, DmThreadSetting, Message, MessageReaction, UserBlock  # noqa: E402


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

        # Opening a thread marks it read — the docstring promised this but the
        # code never did it, so «read» receipts were never earned and the
        # sender's ticks came from a timer on their own screen instead.
        peer_id = request.query_params.get("peer")
        if peer_id:
            unread = DirectMessage.objects.filter(tenant=t, sender_id=peer_id, recipient=me, read=False)
            if unread.exists():
                unread.update(read=True)
                layer = get_channel_layer()
                if layer is not None:
                    # Tell the sender their messages to us are now read.
                    async_to_sync(layer.group_send)(
                        f"dm_{peer_id}", {"type": "dm.read", "message": {"threadId": str(me.id)}}
                    )

        muted_peers = set(
            DmThreadSetting.objects.filter(user=me, muted=True).values_list("peer_id", flat=True)
        )
        blocked_peers = set(UserBlock.objects.filter(user=me).values_list("blocked_id", flat=True))
        qs = DirectMessage.objects.filter(tenant=t).filter(Q(sender=me) | Q(recipient=me)).select_related("sender", "recipient")
        threads = {}
        for m in qs:
            peer = m.recipient if m.sender_id == me.id else m.sender
            th = threads.setdefault(str(peer.id), {
                "id": str(peer.id), "with": peer.name, "avatarColor": peer.avatar_color,
                "online": peer.presence == "online", "messages": [], "unread": 0,
                "muted": peer.id in muted_peers,
                "blocked": peer.id in blocked_peers,
            })
            th["messages"].append({
                "id": str(m.id), "from": "me" if m.sender_id == me.id else "them",
                "text": m.text, "time": m.created_at.strftime("%H:%M"),
                "status": "read" if m.read else "delivered",
                "attachment": m.attachment or None,
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
        attachment = data.get("attachment") or {}
        if not peer or peer.id == me.id or (not text and not attachment):
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "گیرنده یا متن نامعتبر است."}}, status=422)
        # A block stops the conversation in both directions: the blocker must
        # not receive messages, and must not be able to keep sending either.
        if UserBlock.between(me, peer):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "امکان ارسال پیام به این کاربر وجود ندارد."}}, status=403)
        m = DirectMessage.objects.create(
            tenant=request.tenant, sender=me, recipient=peer, text=text, attachment=attachment,
        )
        from apps.notifications.email import notify_direct_message
        notify_direct_message(m)
        # Push to the recipient's live DM socket (from their perspective it's incoming).
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"dm_{peer.id}", {"type": "dm.message", "message": {
                "threadId": str(me.id), "with": me.name, "avatarColor": me.avatar_color,
                "id": str(m.id), "from": "them", "text": m.text, "time": m.created_at.strftime("%H:%M"),
                "attachment": m.attachment or None,
            }})
        return Response({
            "id": str(m.id), "from": "me", "text": m.text,
            "time": m.created_at.strftime("%H:%M"), "status": "delivered",
            "attachment": m.attachment or None,
        }, status=201)


class DmThreadView(APIView):
    """DELETE → clear my copy of a conversation. PATCH {muted} → mute it for me."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, peer_id=None):
        """Removes the whole exchange with this peer.

        A conversation belongs to both sides, so this deletes the messages
        outright rather than hiding them on one screen — the previous UI wiped
        the list locally and the thread reappeared on the next load.
        """
        me = request.user
        t = getattr(request, "tenant", None)
        n, _ = DirectMessage.objects.filter(tenant=t).filter(
            Q(sender=me, recipient_id=peer_id) | Q(sender_id=peer_id, recipient=me)
        ).delete()
        return Response({"deleted": n})

    def patch(self, request, peer_id=None):
        muted = bool((request.data or {}).get("muted"))
        setting, _ = DmThreadSetting.objects.update_or_create(
            user=request.user, peer_id=peer_id,
            defaults={"muted": muted, "tenant": getattr(request, "tenant", None)},
        )
        return Response({"muted": setting.muted})


class UserBlockView(APIView):
    """GET → whom I have blocked. PUT/DELETE {peer} → block or unblock."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = UserBlock.objects.filter(user=request.user).select_related("blocked")
        return Response([
            {"id": str(b.blocked.id), "name": b.blocked.name, "avatarColor": b.blocked.avatar_color}
            for b in rows
        ])

    def put(self, request, peer_id=None):
        peer = User.objects.filter(id=peer_id).first()
        if not peer or peer.id == request.user.id:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "کاربر نامعتبر است."}}, status=422)
        UserBlock.objects.get_or_create(
            user=request.user, blocked=peer,
            defaults={"tenant": getattr(request, "tenant", None)},
        )
        return Response({"blocked": True, "id": str(peer.id), "name": peer.name})

    def delete(self, request, peer_id=None):
        UserBlock.objects.filter(user=request.user, blocked_id=peer_id).delete()
        return Response({"blocked": False, "id": str(peer_id)})


class DmMediaView(APIView):
    """GET → files exchanged in this conversation — «رسانه‌های مشترک»."""
    permission_classes = [IsAuthenticated]

    def get(self, request, peer_id=None):
        me = request.user
        t = getattr(request, "tenant", None)
        qs = (
            DirectMessage.objects.filter(tenant=t)
            .filter(Q(sender=me, recipient_id=peer_id) | Q(sender_id=peer_id, recipient=me))
            .exclude(attachment={})
            .order_by("-created_at")[:60]
        )
        return Response([
            {
                "id": str(m.id),
                "from": "me" if m.sender_id == me.id else "them",
                "time": m.created_at.strftime("%H:%M"),
                **(m.attachment or {}),
            }
            for m in qs if m.attachment
        ])


class CallView(APIView):
    """Call history, and placing a call.

    Media is peer-to-peer (WebRTC); the server only records that the call
    happened and relays the invitation to the callee's live socket.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        me = request.user
        rows = (
            Call.objects.filter(Q(caller=me) | Q(callee=me))
            .select_related("caller", "callee")[:50]
        )
        return Response([
            {
                "id": str(c.id),
                "direction": "out" if c.caller_id == me.id else "in",
                "peer": (c.callee if c.caller_id == me.id else c.caller).name,
                "peerId": str(c.callee_id if c.caller_id == me.id else c.caller_id),
                "kind": c.kind,
                "status": c.status,
                "duration": c.duration_seconds,
                "at": c.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for c in rows
        ])

    def post(self, request):
        me = request.user
        data = request.data or {}
        peer = User.objects.filter(id=data.get("to")).first()
        kind = data.get("kind") if data.get("kind") in ("audio", "video") else "audio"
        if not peer or peer.id == me.id:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "مخاطب نامعتبر است."}}, status=422)
        if UserBlock.between(me, peer):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "امکان تماس با این کاربر وجود ندارد."}}, status=403)

        call = Call.objects.create(tenant=getattr(request, "tenant", None), caller=me, callee=peer, kind=kind)
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"dm_{peer.id}", {"type": "call.invite", "message": {
                "callId": str(call.id), "from": str(me.id), "fromName": me.name,
                "avatarColor": me.avatar_color, "kind": kind,
            }})
        return Response({"id": str(call.id), "status": call.status, "kind": call.kind}, status=201)


class CallDetailView(APIView):
    """PATCH {status} → accept, decline or end a call, and stamp its timing."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, call_id=None):
        from django.utils import timezone

        me = request.user
        call = Call.objects.filter(Q(caller=me) | Q(callee=me), id=call_id).first()
        if not call:
            return Response({"error": {"code": 404, "type": "not_found", "message": "تماس یافت نشد."}}, status=404)

        status_ = (request.data or {}).get("status")
        if status_ not in {"accepted", "declined", "ended", "missed"}:
            return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "وضعیت نامعتبر است."}}, status=422)

        if status_ == "accepted" and call.status == "ringing":
            call.started_at = timezone.now()
        if status_ in {"ended", "declined", "missed"}:
            call.ended_at = timezone.now()
        call.status = status_
        call.save(update_fields=["status", "started_at", "ended_at"])

        # Tell the other side, so their UI leaves the ringing state.
        other = call.callee_id if call.caller_id == me.id else call.caller_id
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"dm_{other}", {"type": "call.state", "message": {
                "callId": str(call.id), "status": call.status,
            }})
        return Response({"id": str(call.id), "status": call.status, "duration": call.duration_seconds})
