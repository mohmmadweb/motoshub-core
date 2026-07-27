from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet
router = DefaultRouter(trailing_slash=False)
router.register("chat/channels", ChannelViewSet, basename="channel")
urlpatterns = router.urls
