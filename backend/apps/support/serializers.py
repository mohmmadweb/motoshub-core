from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)

    class Meta:
        model = TicketMessage
        fields = ["id", "ticket", "author", "from_support", "body", "created_at"]
        read_only_fields = ["id", "author", "created_at"]


class TicketSerializer(serializers.ModelSerializer):
    author = AuthorField(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "number", "subject", "category", "priority", "status",
                  "author", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "number", "author", "messages", "created_at", "updated_at"]
