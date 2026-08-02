from apps.core.viewsets import TenantScopedModelViewSet

from .models import BlogPost, Event, KnowledgeDoc, MediaItem, News
from .serializers import (
    BlogPostSerializer,
    EventSerializer,
    KnowledgeDocSerializer,
    MediaItemSerializer,
    NewsSerializer,
)


def _crud_perms(group: str, *, extra: dict | None = None) -> dict:
    perms = {
        "list": f"{group}.list",
        "retrieve": f"{group}.list",
        "create": f"{group}.create",
        "update": f"{group}.edit",
        "partial_update": f"{group}.edit",
        "destroy": f"{group}.delete",
    }
    if extra:
        perms.update(extra)
    return perms


class NewsViewSet(TenantScopedModelViewSet):
    queryset = News.objects.select_related("author").all()
    serializer_class = NewsSerializer
    required_perms = _crud_perms("news", extra={"pin": "news.pin"})
    filterset_fields = ["visibility", "scope", "pinned", "holding", "company"]
    search_fields = ["title", "summary", "body"]
    ordering_fields = ["created_at", "views", "pinned"]


class BlogViewSet(TenantScopedModelViewSet):
    queryset = BlogPost.objects.select_related("author").all()
    serializer_class = BlogPostSerializer
    required_perms = _crud_perms("blog")
    filterset_fields = ["visibility"]
    search_fields = ["title", "excerpt", "body"]
    ordering_fields = ["created_at", "rating"]


class EventViewSet(TenantScopedModelViewSet):
    queryset = Event.objects.select_related("author").all()
    serializer_class = EventSerializer
    required_perms = _crud_perms("events")
    filterset_fields = ["visibility", "mode"]
    search_fields = ["title", "location", "description"]
    ordering_fields = ["starts_at", "created_at"]


class MediaViewSet(TenantScopedModelViewSet):
    queryset = MediaItem.objects.select_related("author").all()
    serializer_class = MediaItemSerializer
    required_perms = _crud_perms("media", extra={"create": "media.upload"})
    filterset_fields = ["visibility", "kind", "album"]
    search_fields = ["title", "album"]
    ordering_fields = ["created_at", "rating"]


class KnowledgeViewSet(TenantScopedModelViewSet):
    queryset = KnowledgeDoc.objects.select_related("owner").all()
    serializer_class = KnowledgeDocSerializer
    owner_field = "owner"
    required_perms = _crud_perms("knowledge", extra={"create": "knowledge.upload"})
    filterset_fields = ["visibility", "doc_type", "category"]
    search_fields = ["title", "category"]
    ordering_fields = ["created_at"]


# ── Public (unauthenticated) showcase feed ──────────────────────────────────
from rest_framework.permissions import AllowAny  # noqa: E402
from rest_framework.response import Response  # noqa: E402
from rest_framework.views import APIView  # noqa: E402


class PublicFeedView(APIView):
    """Unauthenticated: only visibility=public items. Optional ?domain= to scope."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.tenancy.models import Tenant

        news = News.objects.filter(visibility="public")
        blogs = BlogPost.objects.filter(visibility="public")
        events = Event.objects.filter(visibility="public")
        domain = request.query_params.get("domain")
        if domain:
            tenant = Tenant.objects.filter(domain=domain).first()
            if tenant:
                news = news.filter(tenant=tenant)
                blogs = blogs.filter(tenant=tenant)
                events = events.filter(tenant=tenant)
        return Response({
            "news": NewsSerializer(news.select_related("author")[:10], many=True, context={"request": request}).data,
            "blogs": BlogPostSerializer(blogs.select_related("author")[:10], many=True, context={"request": request}).data,
            "events": EventSerializer(events.select_related("author")[:10], many=True, context={"request": request}).data,
        })
