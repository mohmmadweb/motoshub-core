from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ForumTopicViewSet, FriendsView, GroupViewSet

router = DefaultRouter(trailing_slash=False)
router.register("groups", GroupViewSet, basename="group")
router.register("forum/topics", ForumTopicViewSet, basename="forum-topic")

urlpatterns = router.urls + [
    path("social/friends", FriendsView.as_view(), name="friends"),
]
