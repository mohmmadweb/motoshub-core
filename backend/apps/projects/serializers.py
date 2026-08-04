from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Milestone, Project, Risk, Task, ProjectMember, ProjectExpense, ProjectMinute, PlaybookTemplate


class TaskSerializer(serializers.ModelSerializer):
    assignee = AuthorField(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "project", "title", "status", "assignee", "assignee_id",
                  "priority", "due", "progress", "created_at"]
        read_only_fields = ["id", "assignee", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    open_risks = serializers.SerializerMethodField()
    next_milestone = serializers.SerializerMethodField()

    def get_open_risks(self, obj):
        return obj.risks.exclude(status="closed").count()

    def get_next_milestone(self, obj):
        m = obj.milestones.exclude(status="done").order_by("order").first()
        return {"title": m.title, "due": m.due} if m else None

    manager = AuthorField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "client", "department", "health", "progress", "budget_total",
                  "budget_used", "deadline", "manager", "task_count", "open_risks", "next_milestone",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "manager", "task_count", "open_risks", "next_milestone", "created_at", "updated_at"]


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


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ["id", "project", "name", "role", "allocation"]


class ProjectExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectExpense
        fields = ["id", "project", "title", "category", "amount", "date", "status"]


class ProjectMinuteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMinute
        fields = ["id", "project", "title", "date", "attendees", "decisions", "follow_ups"]


class PlaybookTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybookTemplate
        fields = ["id", "name", "category", "steps", "used_count", "created_at"]
        read_only_fields = ["id", "created_at"]
