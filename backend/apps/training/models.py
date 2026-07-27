from django.db import models

from apps.core.models import TenantScopedModel


class CourseStatus(models.TextChoices):
    OPEN = "open", "ثبت‌نام باز"
    RUNNING = "running", "در حال برگزاری"
    DONE = "done", "برگزار شده"


class TrainingCourse(TenantScopedModel):
    title = models.CharField(max_length=300)
    instructor = models.CharField(max_length=200, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    hours = models.PositiveSmallIntegerField(default=0)
    capacity = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=8, choices=CourseStatus.choices, default=CourseStatus.OPEN)
    satisfaction = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "training_course"

    def __str__(self):
        return self.title

    @property
    def enrolled(self) -> int:
        return self.enrollments.count()


class Enrollment(TenantScopedModel):
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name="enrollments")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="enrollments")
    certificate_issued = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "training_enrollment"
        constraints = [models.UniqueConstraint(fields=["course", "user"], name="uniq_enrollment")]
