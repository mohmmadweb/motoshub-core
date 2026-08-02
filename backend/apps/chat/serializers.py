from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Channel, Message


class MessageSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "channel", "author", "text", "pinned", "reactions", "created_at"]
        read_only_fields = ["id", "author", "reactions", "created_at"]

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
