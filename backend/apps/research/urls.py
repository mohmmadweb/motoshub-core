from rest_framework.routers import DefaultRouter
from .views import ResearchViewSet
router = DefaultRouter(trailing_slash=False)
router.register("research", ResearchViewSet, basename="research")
urlpatterns = router.urls
