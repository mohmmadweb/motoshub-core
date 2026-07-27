from rest_framework.routers import DefaultRouter

from .views import PollViewSet

router = DefaultRouter(trailing_slash=False)
router.register("polls", PollViewSet, basename="poll")
urlpatterns = router.urls
