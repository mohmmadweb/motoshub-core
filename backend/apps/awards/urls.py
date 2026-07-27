from rest_framework.routers import DefaultRouter
from .views import AwardEntryViewSet, AwardTrackViewSet
router = DefaultRouter(trailing_slash=False)
router.register("awards/tracks", AwardTrackViewSet, basename="award-track")
router.register("awards/entries", AwardEntryViewSet, basename="award-entry")
urlpatterns = router.urls
