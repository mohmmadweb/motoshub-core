from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FundViewSet, NfProjectViewSet, ReviewSessionViewSet, FundOverviewView

router = DefaultRouter(trailing_slash=False)
router.register("funds/projects", NfProjectViewSet, basename="nf-project")
router.register("funds/records", FundViewSet, basename="fund")
router.register("funds/review-sessions", ReviewSessionViewSet, basename="review-session")

urlpatterns = router.urls + [
    path("funds/overview", FundOverviewView.as_view(), name="fund-overview"),
]
