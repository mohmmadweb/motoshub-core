from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import ForumReply, ForumTopic, Group


class GroupSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id", "name", "description", "privacy", "color", "category",
            "owner", "member_count", "is_member", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "member_count", "is_member", "created_at", "updated_at"]

    def get_is_member(self, obj) -> bool:
        user = self.context["request"].user
        return obj.memberships.filter(user=user).exists()


class ForumReplySerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = ForumReply
        fields = ["id", "topic", "author", "body", "is_solution", "created_at"]
        read_only_fields = ["id", "author", "is_solution", "created_at"]


class ForumTopicSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ForumTopic
        fields = [
            "id", "title", "body", "author", "group", "category", "views",
            "solved", "visibility", "reply_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "views", "reply_count", "created_at", "updated_at"]
