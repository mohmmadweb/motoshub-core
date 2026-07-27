from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, EventViewSet, KnowledgeViewSet, MediaViewSet, NewsViewSet

router = DefaultRouter(trailing_slash=False)
router.register("news", NewsViewSet, basename="news")
router.register("blogs", BlogViewSet, basename="blog")
router.register("events", EventViewSet, basename="event")
router.register("media", MediaViewSet, basename="media")
router.register("knowledge", KnowledgeViewSet, basename="knowledge")

urlpatterns = router.urls
