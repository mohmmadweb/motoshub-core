from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ForumTopicViewSet, FriendsView, GroupViewSet, PostViewSet
from .group_chat import (
    GroupInviteView,
    GroupJoinByInviteView,
    GroupMemberDetailView,
    GroupMembersView,
    GroupMessageDetailView,
    GroupMessagesView,
    GroupSettingsView,
    GroupTopicDetailView,
    GroupTopicsView,
    GroupTypingView,
)

router = DefaultRouter(trailing_slash=False)
router.register("groups", GroupViewSet, basename="group")
router.register("posts", PostViewSet, basename="post")
router.register("forum/topics", ForumTopicViewSet, basename="forum-topic")

urlpatterns = [
    path("social/friends", FriendsView.as_view(), name="friends"),
    # ── Group conversation (Telegram-grade) ─────────────────────────────────
    path("groups/<uuid:group_id>/messages", GroupMessagesView.as_view(), name="group-messages"),
    path("groups/<uuid:group_id>/messages/<uuid:message_id>", GroupMessageDetailView.as_view(), name="group-message"),
    path("groups/<uuid:group_id>/members", GroupMembersView.as_view(), name="group-members"),
    path("groups/<uuid:group_id>/members/<uuid:user_id>", GroupMemberDetailView.as_view(), name="group-member"),
    path("groups/<uuid:group_id>/invite", GroupInviteView.as_view(), name="group-invite"),
    path("groups/<uuid:group_id>/settings", GroupSettingsView.as_view(), name="group-settings"),
    path("groups/<uuid:group_id>/typing", GroupTypingView.as_view(), name="group-typing"),
    path("groups/<uuid:group_id>/topics", GroupTopicsView.as_view(), name="group-topics"),
    path("groups/<uuid:group_id>/topics/<uuid:topic_id>", GroupTopicDetailView.as_view(), name="group-topic"),
    path("groups/join", GroupJoinByInviteView.as_view(), name="group-join-invite"),
] + router.urls
