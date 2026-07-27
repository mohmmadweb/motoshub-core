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
