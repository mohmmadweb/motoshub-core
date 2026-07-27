from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Channel, Message


class MessageSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "channel", "author", "text", "pinned", "created_at"]
        read_only_fields = ["id", "author", "created_at"]


class ChannelSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)

    class Meta:
        model = Channel
        fields = ["id", "name", "topic", "channel_type", "category", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]
