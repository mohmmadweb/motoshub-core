from rest_framework import serializers

from .models import Challenge, Competition, CompetitionEntry


class EntrySerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    my_vote = serializers.SerializerMethodField()

    class Meta:
        model = CompetitionEntry
        fields = ["id", "by", "title", "color", "votes", "my_vote"]

    def get_votes(self, obj):
        return obj.votes.count()

    def get_my_vote(self, obj):
        user = getattr(self.context.get("request"), "user", None)
        return bool(user and obj.votes.filter(user=user).exists())


class CompetitionSerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True, read_only=True)

    class Meta:
        model = Competition
        fields = ["id", "title", "category", "deadline", "participants", "status", "prize", "entries", "created_at"]
        read_only_fields = ["id", "entries", "created_at"]


class ChallengeSerializer(serializers.ModelSerializer):
    joined = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = ["id", "title", "kind", "category", "progress", "status", "joined", "is_joined", "created_at"]
        read_only_fields = ["id", "joined", "is_joined", "created_at"]

    def get_joined(self, obj):
        return obj.members.count()

    def get_is_joined(self, obj):
        user = getattr(self.context.get("request"), "user", None)
        return bool(user and obj.members.filter(user=user).exists())
