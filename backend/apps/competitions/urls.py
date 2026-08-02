from rest_framework.routers import DefaultRouter

from .views import ChallengeViewSet, CompetitionViewSet

router = DefaultRouter(trailing_slash=False)
router.register("competitions", CompetitionViewSet, basename="competition")
router.register("challenges", ChallengeViewSet, basename="challenge")

urlpatterns = router.urls
