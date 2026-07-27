from rest_framework.routers import DefaultRouter

from .views import NfProjectViewSet

router = DefaultRouter(trailing_slash=False)
router.register("funds/projects", NfProjectViewSet, basename="nf-project")

urlpatterns = router.urls
