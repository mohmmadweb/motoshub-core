from rest_framework.routers import DefaultRouter

from .views import (
    PendingReviewItemViewSet,
    ContractViewSet,
    ESignDocumentViewSet,
    TechTransferViewSet,
    TenderViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("contracts/tech-transfer", TechTransferViewSet, basename="tech-transfer")
router.register("contracts/tenders", TenderViewSet, basename="tender")
router.register("contracts/esign", ESignDocumentViewSet, basename="esign")
router.register("contracts/pending-review", PendingReviewItemViewSet, basename="pending-review")
router.register("contracts", ContractViewSet, basename="contract")

urlpatterns = router.urls
