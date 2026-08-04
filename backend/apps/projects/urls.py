from rest_framework.routers import DefaultRouter

from .views import MilestoneViewSet, RiskViewSet, ProjectViewSet, TaskViewSet, ProjectMemberViewSet, ProjectExpenseViewSet, ProjectMinuteViewSet, PlaybookTemplateViewSet

router = DefaultRouter(trailing_slash=False)
router.register("project-members", ProjectMemberViewSet, basename="project-member")
router.register("project-expenses", ProjectExpenseViewSet, basename="project-expense")
router.register("project-minutes", ProjectMinuteViewSet, basename="project-minute")
router.register("playbooks", PlaybookTemplateViewSet, basename="playbook")
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("milestones", MilestoneViewSet, basename="milestone")
router.register("risks", RiskViewSet, basename="risk")

urlpatterns = router.urls
