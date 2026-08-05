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
    # The description someone types when opening a ticket. It is not a column on
    # Ticket — it becomes the thread's first message, so the conversation reads
    # in order instead of starting with an unexplained subject line.
    body = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Ticket
        fields = ["id", "number", "subject", "category", "priority", "status",
                  "author", "body", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "number", "author", "messages", "created_at", "updated_at"]
