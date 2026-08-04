from rest_framework.routers import DefaultRouter

from django.urls import path

from .views import (BlogViewSet, EventViewSet, KnowledgeViewSet, MediaViewSet, NewsViewSet, PublicFeedView,
                    ContentCommentViewSet, PublicationIssueViewSet, RndDocViewSet, SupportedProductViewSet,
                    SupportedVentureViewSet, PartnerTechnologistViewSet)

router = DefaultRouter(trailing_slash=False)
router.register("comments", ContentCommentViewSet, basename="comment")
router.register("publications", PublicationIssueViewSet, basename="publication")
router.register("knowledge/rnd-docs", RndDocViewSet, basename="rnd-doc")
router.register("knowledge/products", SupportedProductViewSet, basename="supported-product")
router.register("knowledge/ventures", SupportedVentureViewSet, basename="supported-venture")
router.register("knowledge/technologists", PartnerTechnologistViewSet, basename="partner-technologist")
router.register("news", NewsViewSet, basename="news")
router.register("blogs", BlogViewSet, basename="blog")
router.register("events", EventViewSet, basename="event")
router.register("media", MediaViewSet, basename="media")
router.register("knowledge", KnowledgeViewSet, basename="knowledge")

urlpatterns = [path("public/feed", PublicFeedView.as_view(), name="public-feed")] + router.urls
