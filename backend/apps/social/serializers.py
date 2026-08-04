from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import ForumReply, ForumTopic, Group, Post, GroupMembership


class GroupSerializer(serializers.ModelSerializer):
    unread = serializers.SerializerMethodField()

    def get_unread(self, obj):
        """Messages in this group the caller hasn't seen yet."""
        user = getattr(self.context.get("request"), "user", None)
        channel = getattr(obj, "channel", None)
        if not user or not getattr(user, "is_authenticated", False) or channel is None:
            return 0
        row = obj.memberships.filter(user=user).first()
        if row is None:
            return 0
        qs = channel.messages.exclude(author=user).exclude(deleted=True)
        if row.last_read_at:
            qs = qs.filter(created_at__gt=row.last_read_at)
        return qs.count()

    owner = AuthorField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id", "name", "description", "privacy", "color", "category",
            "owner", "member_count", "is_member", "unread", "invite_code", "slow_mode_seconds",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "member_count", "is_member", "unread", "invite_code", "created_at", "updated_at"]

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


class PostSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True, default="")
    likes = serializers.SerializerMethodField()
    my_like = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "group", "group_name", "content", "tags", "pinned",
                  "attachment", "likes", "my_like", "comments", "created_at"]
        read_only_fields = ["id", "author", "group_name", "likes", "my_like", "comments", "created_at"]

    def get_likes(self, obj):
        return obj.post_likes.count()

    def get_my_like(self, obj):
        user = getattr(self.context.get("request"), "user", None)
        return bool(user and obj.post_likes.filter(user=user).exists())

    def get_comments(self, obj):
        return obj.post_comments.count()


class GroupMemberSerializer(serializers.ModelSerializer):
    """A member row for the group's member panel."""
    user = AuthorField(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    name = serializers.CharField(source="user.name", read_only=True)
    title = serializers.CharField(source="user.title", read_only=True)
    presence = serializers.CharField(source="user.presence", read_only=True)
    can_moderate = serializers.BooleanField(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ["id", "user", "user_id", "name", "title", "presence", "role",
                  "muted", "banned", "can_moderate", "created_at"]
        read_only_fields = ["id", "user", "name", "title", "presence", "can_moderate", "created_at"]
