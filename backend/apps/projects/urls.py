from rest_framework.routers import DefaultRouter

from .views import MilestoneViewSet, RiskViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter(trailing_slash=False)
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("milestones", MilestoneViewSet, basename="milestone")
router.register("risks", RiskViewSet, basename="risk")

urlpatterns = router.urls
