"""Realtime chat consumer. Auth via ?token=<jwt> query param; group per channel."""
import json

import jwt
from django.core.exceptions import ValidationError
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.accounts.tokens import decode


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @classmethod
    async def encode_json(cls, content):
        # UUID/Decimal/datetime-safe encoding (serializer output isn't plain JSON).
        return json.dumps(content, default=str, ensure_ascii=False)

    async def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        user = await self._authenticate()
        if user is None or not await self._can_view(user, self.channel_id):
            await self.close(code=4401)
            return
        self.user = user
        self.group = f"chat_{self.channel_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content):
        text = (content or {}).get("text", "").strip()
        if not text:
            return
        data = await self._save(text)
        await self.channel_layer.group_send(self.group, {"type": "chat.message", "message": data})

    async def chat_message(self, event):
        await self.send_json(event["message"])

    async def chat_typing(self, event):
        """Someone is typing — transient, not persisted."""
        await self.send_json({"type": "typing", **event["message"]})

    # ── helpers ──────────────────────────────────────────────────────────────
    async def _authenticate(self):
        qs = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        token = params.get("token")
        if not token:
            return None
        try:
            payload = decode(token)
        except jwt.InvalidTokenError:
            return None
        return await self._get_user(payload.get("sub"))

    @database_sync_to_async
    def _get_user(self, user_id):
        from apps.accounts.models import User
        return User.objects.filter(id=user_id, is_active=True).first()

    @database_sync_to_async
    def _can_view(self, user, channel_id):
        from .models import Channel
        return Channel.objects.filter(id=channel_id, tenant=user.tenant).exists()

    @database_sync_to_async
    def _save(self, text):
        from .models import Channel, Message
        from .serializers import MessageSerializer
        channel = Channel.objects.get(id=self.channel_id)
        msg = Message.objects.create(channel=channel, author=self.user, text=text, tenant=channel.tenant)
        return MessageSerializer(msg).data


class DmConsumer(AsyncJsonWebsocketConsumer):
    """Per-user DM socket: joins group dm_<user_id>; receives messages addressed
    to this user (broadcast by DmView on POST). Send still goes over REST."""

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, default=str, ensure_ascii=False)

    async def connect(self):
        user = await self._authenticate()
        if user is None:
            await self.close(code=4401)
            return
        self.user = user
        self.group = f"dm_{user.id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def dm_message(self, event):
        await self.send_json(event["message"])

    async def dm_read(self, event):
        """The peer opened our thread — their side marked our messages read."""
        await self.send_json({"type": "read", **event["message"]})

    async def dm_typing(self, event):
        """The peer is composing. Transient: never stored, never replayed."""
        await self.send_json({"type": "typing", **event["message"]})

    async def call_invite(self, event):
        """Someone is ringing this user."""
        await self.send_json({"type": "call:invite", **event["message"]})

    async def call_state(self, event):
        """The other side accepted, declined or hung up."""
        await self.send_json({"type": "call:state", **event["message"]})

    async def call_signal(self, event):
        """A WebRTC offer/answer/ICE candidate addressed to this user."""
        await self.send_json({"type": "call:signal", **event["message"]})

    async def receive_json(self, content):
        """Typing pings and WebRTC signalling; messages still go over REST.

        Every relay stamps this socket's authenticated identity as the sender,
        so a client cannot impersonate someone else — neither to fake a typing
        indicator nor to inject signalling into a call it is not part of.
        """
        content = content or {}
        kind = content.get("type")
        peer = content.get("to")
        if not peer:
            return

        if kind == "typing":
            await self.channel_layer.group_send(
                f"dm_{peer}", {"type": "dm.typing", "message": {"from": str(self.user.id)}}
            )
            return

        if kind == "call:signal":
            # The SDP/ICE payload is opaque to the server; it is forwarded as-is
            # so the two browsers can negotiate a direct connection. Media never
            # passes through here.
            call_id = content.get("callId")
            if not call_id or not await self._in_call(call_id):
                return
            await self.channel_layer.group_send(f"dm_{peer}", {"type": "call.signal", "message": {
                "callId": str(call_id),
                "from": str(self.user.id),
                "signal": content.get("signal"),
            }})

    @database_sync_to_async
    def _in_call(self, call_id) -> bool:
        """Only the two participants may relay signalling for a call."""
        from django.db.models import Q

        from .models import Call

        try:
            return Call.objects.filter(
                Q(caller=self.user) | Q(callee=self.user), id=call_id
            ).exists()
        except (ValueError, ValidationError):
            return False

    async def _authenticate(self):
        qs = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        token = params.get("token")
        if not token:
            return None
        try:
            payload = decode(token)
        except jwt.InvalidTokenError:
            return None
        return await self._get_user(payload.get("sub"))

    @database_sync_to_async
    def _get_user(self, user_id):
        from apps.accounts.models import User
        return User.objects.filter(id=user_id, is_active=True).first()
