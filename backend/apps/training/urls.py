from rest_framework.routers import DefaultRouter

from .views import TrainingCourseViewSet

router = DefaultRouter(trailing_slash=False)
router.register("training/courses", TrainingCourseViewSet, basename="course")
urlpatterns = router.urls
