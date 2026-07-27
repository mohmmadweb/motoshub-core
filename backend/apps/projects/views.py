from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


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
    owner_field = None  # tasks aren't owned by their creator
    required_perms = {
        "list": "projects.tasks", "retrieve": "projects.tasks",
        "create": "projects.tasks", "update": "projects.tasks",
        "partial_update": "projects.tasks", "destroy": "projects.tasks",
    }
    filterset_fields = ["project", "status", "priority", "assignee"]
    search_fields = ["title"]
