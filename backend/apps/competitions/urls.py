from rest_framework.routers import DefaultRouter

from .views import ChallengeViewSet, CompetitionEntryViewSet, CompetitionViewSet

router = DefaultRouter(trailing_slash=False)
router.register("competitions", CompetitionViewSet, basename="competition")
router.register("challenges", ChallengeViewSet, basename="challenge")
router.register("competition-entries", CompetitionEntryViewSet, basename="competition-entry")

urlpatterns = router.urls
