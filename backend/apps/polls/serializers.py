from rest_framework import serializers

from .models import Poll, PollOption, Quiz


class PollOptionSerializer(serializers.ModelSerializer):
    votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = PollOption
        fields = ["id", "label", "votes"]


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    my_vote = serializers.SerializerMethodField()
    option_labels = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Poll
        fields = ["id", "question", "ends_at", "group", "options", "my_vote", "option_labels", "created_at"]
        read_only_fields = ["id", "options", "my_vote", "created_at"]

    def get_my_vote(self, obj):
        v = obj.votes.filter(user=self.context["request"].user).first()
        return str(v.option_id) if v else None

    def create(self, validated_data):
        labels = validated_data.pop("option_labels", [])
        poll = super().create(validated_data)
        for label in labels:
            PollOption.objects.create(poll=poll, label=label, tenant=poll.tenant)
        return poll


class QuizSerializer(serializers.ModelSerializer):
    my_score = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions", "minutes", "deadline", "status",
                  "passing", "my_score", "participants", "created_at"]
        read_only_fields = ["id", "my_score", "participants", "created_at"]

    def get_my_score(self, obj):
        user = getattr(self.context.get("request"), "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return None
        attempt = obj.attempts.filter(user=user).first()
        return attempt.score if attempt else None

    def get_participants(self, obj):
        return obj.attempts.count()
