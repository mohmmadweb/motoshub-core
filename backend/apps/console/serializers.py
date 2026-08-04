from rest_framework import serializers

from .models import WorkflowSettings, SavedReport, Integration, GuestAccount


class WorkflowSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowSettings
        exclude = ["id", "tenant", "created_at", "updated_at"]


class SavedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedReport
        fields = ["id", "name", "module", "group_by", "schedule", "last_run", "format", "created_at"]
        read_only_fields = ["id", "created_at"]


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ["id", "name", "integration_type", "channel", "active", "created_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class GuestAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestAccount
        fields = ["id", "name", "org", "channels", "expires", "created_at"]
        read_only_fields = ["id", "created_at"]
