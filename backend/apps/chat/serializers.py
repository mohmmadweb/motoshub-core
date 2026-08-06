from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Channel, Message


class ReplyPreviewSerializer(serializers.ModelSerializer):
    """Compact quote of the message being replied to."""
    author = AuthorField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "author", "text", "deleted"]


class MessageSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)
    reactions = serializers.SerializerMethodField()
    reply_to = ReplyPreviewSerializer(read_only=True)
    reply_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    thread_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "channel", "author", "text", "pinned", "reactions", "reply_to", "reply_to_id",
                  "thread_count", "edited_at", "deleted", "forwarded_from", "attachment", "mentions", "created_at"]
        read_only_fields = ["id", "author", "reactions", "reply_to", "thread_count", "edited_at", "created_at"]

    def get_thread_count(self, obj):
        """How many messages reply to this one — the thread's real size."""
        return obj.replies.count() if hasattr(obj, "replies") else 0

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.deleted:  # never leak the original text of a deleted message
            data["text"] = ""
            data["attachment"] = None
        return data

    def get_reactions(self, obj):
        me = getattr(self.context.get("request"), "user", None)
        agg = {}
        for r in obj.reactions.all():
            e = agg.setdefault(r.icon, {"icon": r.icon, "count": 0, "reactedByMe": False})
            e["count"] += 1
            if me and r.user_id == getattr(me, "id", None):
                e["reactedByMe"] = True
        return list(agg.values())


class ChannelSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)

    class Meta:
        model = Channel
        fields = ["id", "name", "topic", "channel_type", "category", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]
