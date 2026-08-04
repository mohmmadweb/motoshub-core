from rest_framework import serializers

from .models import WorkflowSettings, SavedReport


class WorkflowSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowSettings
        exclude = ["id", "tenant", "created_at", "updated_at"]


class SavedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedReport
        fields = ["id", "name", "module", "group_by", "schedule", "last_run", "format", "created_at"]
        read_only_fields = ["id", "created_at"]
