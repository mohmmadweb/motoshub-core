from rest_framework import serializers

from .models import ResearchApplication, ResearchOpportunity


class ResearchApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchApplication
        fields = ["id", "opportunity", "applicant_name", "affiliation", "score", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class ResearchOpportunitySerializer(serializers.ModelSerializer):
    applicant_count = serializers.IntegerField(read_only=True)
    applications = ResearchApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchOpportunity
        fields = ["id", "title", "field", "stage", "budget", "supervisor", "deadline",
                  "applicant_count", "applications", "created_at", "updated_at"]
        read_only_fields = ["id", "applicant_count", "applications", "created_at", "updated_at"]
