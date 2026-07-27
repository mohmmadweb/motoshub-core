from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.content.views import _crud_perms
from apps.core.viewsets import TenantScopedModelViewSet

from .models import ForumReply, ForumTopic, Group, GroupMembership
from .serializers import ForumReplySerializer, ForumTopicSerializer, GroupSerializer


class GroupViewSet(TenantScopedModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.select_related("owner").all()
    owner_field = "owner"
    required_perms = _crud_perms("groups", extra={"join": "groups.list", "leave": "groups.list"})
    filterset_fields = ["privacy", "category"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        # Tenant scoping + IDOR-safe privacy: private groups are visible only to
        # members, the owner, or a groups-moderator.
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or "groups.edit" in user.get_permission_ids(self.request.tenant):
            return qs
        return qs.filter(
            Q(privacy="public")
            | Q(owner=user)
            | Q(memberships__user=user)
        ).distinct()

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        group = self.get_object()
        GroupMembership.objects.get_or_create(group=group, user=request.user, tenant=request.tenant)
        return Response({"joined": True, "member_count": group.member_count})

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        group = self.get_object()
        GroupMembership.objects.filter(group=group, user=request.user).delete()
        return Response({"joined": False, "member_count": group.member_count})


class ForumTopicViewSet(TenantScopedModelViewSet):
    serializer_class = ForumTopicSerializer
    queryset = ForumTopic.objects.select_related("author").all()
    required_perms = _crud_perms("forum", extra={
        "create": "forum.create", "reply": "forum.reply", "solve": "forum.solve",
    })
    filterset_fields = ["solved", "visibility", "group", "category"]
    search_fields = ["title", "body"]

    @action(detail=True, methods=["get", "post"])
    def replies(self, request, pk=None):
        topic = self.get_object()
        if request.method == "POST":
            body = (request.data or {}).get("body", "").strip()
            if not body:
                return Response({"error": {"code": 422, "type": "unprocessable_entity", "message": "متن پاسخ الزامی است."}}, status=422)
            reply = ForumReply.objects.create(topic=topic, author=request.user, body=body, tenant=request.tenant)
            return Response(ForumReplySerializer(reply, context={"request": request}).data, status=201)
        qs = topic.replies.select_related("author").all()
        return Response(ForumReplySerializer(qs, many=True, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def solve(self, request, pk=None):
        topic = self.get_object()
        topic.solved = True
        topic.save(update_fields=["solved"])
        return Response({"solved": True})
