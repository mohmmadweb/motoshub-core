"""Projects: a project with a health signal, budget, and a Kanban task board."""
from django.db import models

from apps.core.models import TenantScopedModel


class Health(models.TextChoices):
    GREEN = "green", "سبز"
    YELLOW = "yellow", "زرد"
    RED = "red", "قرمز"


class Project(TenantScopedModel):
    name = models.CharField(max_length=300)
    client = models.CharField(max_length=200, blank=True)
    health = models.CharField(max_length=6, choices=Health.choices, default=Health.GREEN)
    progress = models.PositiveSmallIntegerField(default=0)
    budget_total = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    budget_used = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    deadline = models.DateField(null=True, blank=True)
    manager = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="managed_projects")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="created_projects")

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_project"

    def __str__(self):
        return self.name

    @property
    def task_count(self) -> int:
        return self.tasks.count()


class TaskStatus(models.TextChoices):
    PLANNING = "planning", "برنامه‌ریزی"
    IN_PROGRESS = "in_progress", "در حال انجام"
    REVIEW = "review", "بازبینی"
    DONE = "done", "انجام‌شده"


class Priority(models.TextChoices):
    LOW = "low", "کم"
    MEDIUM = "medium", "متوسط"
    HIGH = "high", "زیاد"


class Task(TenantScopedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=300)
    status = models.CharField(max_length=12, choices=TaskStatus.choices, default=TaskStatus.PLANNING)
    assignee = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.MEDIUM)
    due = models.DateField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_task"
        ordering = ["created_at"]

    def __str__(self):
        return self.title
