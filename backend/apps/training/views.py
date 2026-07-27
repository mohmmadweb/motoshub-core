from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.viewsets import TenantScopedModelViewSet

from .models import Enrollment, TrainingCourse
from .serializers import TrainingCourseSerializer


class TrainingCourseViewSet(TenantScopedModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer
    owner_field = None
    required_perms = {
        "list": "training.list", "retrieve": "training.list", "create": "training.create",
        "update": "training.create", "partial_update": "training.create", "destroy": "training.create",
        "enroll": "training.enroll", "leave": "training.enroll",
    }
    filterset_fields = ["status"]
    search_fields = ["title", "instructor"]

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        course = self.get_object()
        Enrollment.objects.get_or_create(course=course, user=request.user, tenant=request.tenant)
        return Response({"enrolled": True, "count": course.enrolled})

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        course = self.get_object()
        Enrollment.objects.filter(course=course, user=request.user).delete()
        return Response({"enrolled": False, "count": course.enrolled})
