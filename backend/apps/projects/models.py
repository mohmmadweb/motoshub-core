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
    department = models.CharField(max_length=120, blank=True, help_text="معاونت/دپارتمان مالک پروژه")
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


class Milestone(TenantScopedModel):
    """Project milestone (the board's «نقاط عطف» tab)."""
    STATUS = [("done", "انجام‌شده"), ("in_progress", "در حال انجام"),
              ("upcoming", "پیش‌رو"), ("at_risk", "در خطر")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=300)
    due = models.CharField(max_length=20, blank=True, help_text="سررسید (جلالی نمایشی)")
    status = models.CharField(max_length=12, choices=STATUS, default="upcoming")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_milestone"
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.title


class Risk(TenantScopedModel):
    """Project risk register (the board's «ریسک‌ها» tab)."""
    SEVERITY = [("low", "کم"), ("medium", "متوسط"), ("critical", "بحرانی")]
    PROBABILITY = [("low", "کم"), ("medium", "متوسط"), ("high", "زیاد")]
    STATUS = [("open", "باز"), ("mitigating", "در حال رفع"), ("closed", "بسته")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="risks")
    title = models.CharField(max_length=300)
    severity = models.CharField(max_length=8, choices=SEVERITY, default="medium")
    probability = models.CharField(max_length=6, choices=PROBABILITY, default="medium")
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    owner = models.CharField(max_length=200, blank=True)
    mitigation = models.TextField(blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_risk"

    def __str__(self):
        return self.title


class ProjectMember(TenantScopedModel):
    """Someone allocated to a project (team tab)."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=120, blank=True)
    allocation = models.PositiveSmallIntegerField(default=0, help_text="درصد تخصیص")

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_member"


class ProjectExpense(TenantScopedModel):
    STATUS = [("paid", "پرداخت‌شده"), ("pending", "در انتظار تأیید"), ("planned", "برنامه‌ریزی‌شده")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=120, blank=True)
    amount = models.CharField(max_length=80, blank=True)
    date = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=8, choices=STATUS, default="planned")

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_expense"


class ProjectMinute(TenantScopedModel):
    """Meeting minutes attached to a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="minutes")
    title = models.CharField(max_length=300)
    date = models.CharField(max_length=20, blank=True)
    attendees = models.PositiveSmallIntegerField(default=0)
    decisions = models.PositiveSmallIntegerField(default=0)
    follow_ups = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_minute"


class PlaybookTemplate(TenantScopedModel):
    """Reusable project template (playbook)."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=120, blank=True)
    steps = models.PositiveSmallIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "projects_playbook"

    def __str__(self):
        return self.name
