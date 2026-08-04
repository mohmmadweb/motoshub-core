from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import Milestone, Project, Risk, Task, ProjectMember, ProjectExpense, ProjectMinute, PlaybookTemplate
from apps.notifications.services import notify

from .serializers import MilestoneSerializer, ProjectSerializer, RiskSerializer, TaskSerializer, ProjectMemberSerializer, ProjectExpenseSerializer, ProjectMinuteSerializer, PlaybookTemplateSerializer


class ProjectViewSet(TenantScopedModelViewSet):
    queryset = Project.objects.select_related("manager").all()
    serializer_class = ProjectSerializer
    required_perms = _crud_perms("projects")
    filterset_fields = ["health"]
    search_fields = ["name", "client"]
    ordering_fields = ["created_at", "progress", "deadline"]


class TaskViewSet(TenantScopedModelViewSet):
    queryset = Task.objects.select_related("assignee", "project").all()
    serializer_class = TaskSerializer
    owner_field = None

    def perform_create(self, serializer):
        task = serializer.save(tenant=getattr(self.request, "tenant", None))
        if task.assignee and task.assignee != self.request.user:
            notify(task.assignee, f"وظیفهٔ «{task.title}» به شما واگذار شد.", kind="task", tenant=self.request.tenant)  # tasks aren't owned by their creator
    required_perms = {
        "list": "projects.tasks", "retrieve": "projects.tasks",
        "create": "projects.tasks", "update": "projects.tasks",
        "partial_update": "projects.tasks", "destroy": "projects.tasks",
    }
    filterset_fields = ["project", "status", "priority", "assignee"]
    search_fields = ["title"]


class MilestoneViewSet(TenantScopedModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    filterset_fields = ["project", "status"]
    search_fields = ["title"]


class RiskViewSet(TenantScopedModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    filterset_fields = ["project", "status", "severity"]
    search_fields = ["title", "owner"]


class ProjectMemberViewSet(TenantScopedModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    filterset_fields = ["project"]


class ProjectExpenseViewSet(TenantScopedModelViewSet):
    queryset = ProjectExpense.objects.all()
    serializer_class = ProjectExpenseSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    filterset_fields = ["project", "status"]


class ProjectMinuteViewSet(TenantScopedModelViewSet):
    queryset = ProjectMinute.objects.all()
    serializer_class = ProjectMinuteSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    filterset_fields = ["project"]


class PlaybookTemplateViewSet(TenantScopedModelViewSet):
    queryset = PlaybookTemplate.objects.all()
    serializer_class = PlaybookTemplateSerializer
    owner_field = None
    required_perms = _crud_perms("projects")
    search_fields = ["name", "category"]
