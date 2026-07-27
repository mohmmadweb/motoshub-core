from rest_framework import serializers

from .models import TrainingCourse


class TrainingCourseSerializer(serializers.ModelSerializer):
    enrolled = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = TrainingCourse
        fields = ["id", "title", "instructor", "starts_at", "hours", "capacity",
                  "status", "satisfaction", "enrolled", "is_enrolled", "created_at"]
        read_only_fields = ["id", "enrolled", "is_enrolled", "created_at"]

    def get_is_enrolled(self, obj) -> bool:
        return obj.enrollments.filter(user=self.context["request"].user).exists()
