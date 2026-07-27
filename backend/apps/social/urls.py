from rest_framework.routers import DefaultRouter

from .views import ForumTopicViewSet, GroupViewSet

router = DefaultRouter(trailing_slash=False)
router.register("groups", GroupViewSet, basename="group")
router.register("forum/topics", ForumTopicViewSet, basename="forum-topic")

urlpatterns = router.urls
