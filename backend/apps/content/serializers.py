from rest_framework import serializers

from .models import BlogPost, Event, KnowledgeDoc, MediaItem, News, PublicationIssue, RndDoc, SupportedProduct, SupportedVenture, PartnerTechnologist, ContentComment


class AuthorField(serializers.Serializer):
    """Compact read-only author/owner representation."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    avatar_color = serializers.CharField()


class NewsSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = News
        fields = [
            "id", "title", "topic", "summary", "body", "author", "pinned", "views",
            "comment_count", "visibility", "scope", "holding", "company",
            "created_at", "updated_at", "image"]
        read_only_fields = ["id", "author", "views", "comment_count", "created_at", "updated_at"]


class BlogPostSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = BlogPost
        fields = ["id", "title", "author", "excerpt", "body", "rating", "tags", "visibility", "created_at", "updated_at", "image"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class EventSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "starts_at", "location", "description", "attendees",
            "capacity", "category", "hashtags", "mode", "join_link", "map_url",
            "author", "visibility", "created_at", "updated_at", "image"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class MediaItemSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = MediaItem
        fields = ["id", "kind", "title", "album", "file", "color", "rating", "duration", "tags", "author", "visibility", "created_at", "updated_at", "image"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class KnowledgeDocSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)

    class Meta:
        model = KnowledgeDoc
        fields = ["id", "title", "category", "doc_type", "file", "size", "owner", "visibility", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


# ── Publications / R&D docs / registries ────────────────────────────────────
class PublicationIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationIssue
        fields = ["id", "magazine", "issue_no", "title", "season", "stage", "articles", "created_at"]
        read_only_fields = ["id", "created_at"]


class RndDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = RndDoc
        fields = ["id", "company", "holding", "progress", "status_label", "obstacles", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupportedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedProduct
        fields = ["id", "name", "company", "trl", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupportedVentureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedVenture
        fields = ["id", "name", "support_type", "field", "year", "created_at"]
        read_only_fields = ["id", "created_at"]


class PartnerTechnologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerTechnologist
        fields = ["id", "name", "expertise", "projects", "rating", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContentCommentSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = ContentComment
        fields = ["id", "kind", "object_id", "author", "body", "accepted", "created_at"]
        read_only_fields = ["id", "author", "created_at"]
