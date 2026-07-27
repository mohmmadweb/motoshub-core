from rest_framework import serializers

from .models import BlogPost, Event, KnowledgeDoc, MediaItem, News


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
            "id", "title", "summary", "body", "author", "pinned", "views",
            "comment_count", "visibility", "scope", "holding", "company",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "views", "comment_count", "created_at", "updated_at"]


class BlogPostSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = BlogPost
        fields = ["id", "title", "author", "excerpt", "body", "rating", "tags", "visibility", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class EventSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "starts_at", "location", "description", "attendees",
            "hashtags", "mode", "join_link", "map_url", "author", "visibility",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class MediaItemSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = MediaItem
        fields = ["id", "kind", "title", "album", "file", "color", "rating", "tags", "author", "visibility", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class KnowledgeDocSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)

    class Meta:
        model = KnowledgeDoc
        fields = ["id", "title", "category", "doc_type", "file", "size", "owner", "visibility", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
