from rest_framework.routers import DefaultRouter
from .views import ResearchViewSet, RfpCallViewSet, SabbaticalViewSet
router = DefaultRouter(trailing_slash=False)
router.register("research/rfp", RfpCallViewSet, basename="rfp")
router.register("research/sabbaticals", SabbaticalViewSet, basename="sabbatical")
router.register("research", ResearchViewSet, basename="research")
urlpatterns = router.urls
