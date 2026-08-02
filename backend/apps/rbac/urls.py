from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import AssignmentViewSet, PermissionCatalogView, RoleViewSet

router = DefaultRouter(trailing_slash=False)
router.register("roles", RoleViewSet, basename="role")
router.register("role-assignments", AssignmentViewSet, basename="role-assignment")

urlpatterns = [path("permissions/catalog", PermissionCatalogView.as_view(), name="perm-catalog")] + router.urls
