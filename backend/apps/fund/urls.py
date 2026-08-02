from rest_framework.routers import DefaultRouter

from .views import FundViewSet, NfProjectViewSet

router = DefaultRouter(trailing_slash=False)
router.register("funds/projects", NfProjectViewSet, basename="nf-project")
router.register("funds/records", FundViewSet, basename="fund")

urlpatterns = router.urls
