"""Realtime chat consumer. Auth via ?token=<jwt> query param; group per channel."""
import json

import jwt
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

    async def receive_json(self, content):
        """Only a typing ping travels this way; sending still goes over REST.

        Relayed straight to the addressed peer with this socket's authenticated
        identity — the client cannot claim to be someone else typing.
        """
        if (content or {}).get("type") != "typing":
            return
        peer = (content or {}).get("to")
        if not peer:
            return
        await self.channel_layer.group_send(
            f"dm_{peer}", {"type": "dm.typing", "message": {"from": str(self.user.id)}}
        )

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
