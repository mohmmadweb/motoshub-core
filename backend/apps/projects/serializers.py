from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Milestone, Project, Risk, Task


class TaskSerializer(serializers.ModelSerializer):
    assignee = AuthorField(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "project", "title", "status", "assignee", "assignee_id",
                  "priority", "due", "progress", "created_at"]
        read_only_fields = ["id", "assignee", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    manager = AuthorField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "client", "department", "health", "progress", "budget_total",
                  "budget_used", "deadline", "manager", "task_count", "created_at", "updated_at"]
        read_only_fields = ["id", "manager", "task_count", "created_at", "updated_at"]


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ["id", "project", "title", "due", "status", "order", "created_at"]
        read_only_fields = ["id", "created_at"]


class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = ["id", "project", "title", "severity", "probability", "status",
                  "owner", "mitigation", "created_at"]
        read_only_fields = ["id", "created_at"]
