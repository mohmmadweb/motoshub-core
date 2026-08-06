from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CallDetailView, CallView, ChannelViewSet, DmMediaView, DmThreadView, DmView,
    MessageReactView, UserBlockView,
)

router = DefaultRouter(trailing_slash=False)
router.register("chat/channels", ChannelViewSet, basename="channel")

urlpatterns = router.urls + [
    path("chat/dms", DmView.as_view(), name="chat-dms"),
    path("chat/dms/<uuid:peer_id>", DmThreadView.as_view(), name="chat-dm-thread"),
    path("chat/dms/<uuid:peer_id>/media", DmMediaView.as_view(), name="chat-dm-media"),
    path("chat/blocks", UserBlockView.as_view(), name="chat-blocks"),
    path("chat/blocks/<uuid:peer_id>", UserBlockView.as_view(), name="chat-block"),
    path("chat/calls", CallView.as_view(), name="chat-calls"),
    path("chat/calls/<uuid:call_id>", CallDetailView.as_view(), name="chat-call"),
    path("chat/messages/<uuid:message_id>/react", MessageReactView.as_view(), name="chat-react"),
]
