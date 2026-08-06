from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChannelViewSet, DmThreadView, DmView, MessageReactView

router = DefaultRouter(trailing_slash=False)
router.register("chat/channels", ChannelViewSet, basename="channel")

urlpatterns = router.urls + [
    path("chat/dms", DmView.as_view(), name="chat-dms"),
    path("chat/dms/<uuid:peer_id>", DmThreadView.as_view(), name="chat-dm-thread"),
    path("chat/messages/<uuid:message_id>/react", MessageReactView.as_view(), name="chat-react"),
]
