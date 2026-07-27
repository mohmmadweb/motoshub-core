from rest_framework import serializers
from .models import AwardEntry, AwardTrack


class AwardEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AwardEntry
        fields = ["id", "track", "title", "company", "status", "score", "edit_used", "created_at"]
        read_only_fields = ["id", "edit_used", "created_at"]


class AwardTrackSerializer(serializers.ModelSerializer):
    entries = AwardEntrySerializer(many=True, read_only=True)
    submission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AwardTrack
        fields = ["id", "title", "categories", "submission_count", "entries", "created_at"]
        read_only_fields = ["id", "submission_count", "entries", "created_at"]
