from rest_framework import serializers

from .models import WorkflowSettings


class WorkflowSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowSettings
        exclude = ["id", "tenant", "created_at", "updated_at"]
