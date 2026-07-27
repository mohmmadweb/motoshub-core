from rest_framework.routers import DefaultRouter

from .views import ContractViewSet

router = DefaultRouter(trailing_slash=False)
router.register("contracts", ContractViewSet, basename="contract")

urlpatterns = router.urls
