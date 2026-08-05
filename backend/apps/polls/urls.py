from rest_framework.routers import DefaultRouter

from .views import PollViewSet, QuizViewSet

router = DefaultRouter(trailing_slash=False)
router.register("polls", PollViewSet, basename="poll")
router.register("quizzes", QuizViewSet, basename="quiz")
urlpatterns = router.urls
