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


# ── Friends & Follow (personal social graph) ────────────────────────────────
from rest_framework.permissions import IsAuthenticated  # noqa: E402
from rest_framework.views import APIView  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from .models import Follow, Friendship  # noqa: E402


class FriendsView(APIView):
    """The current user's friend graph, as the prototype Friends page expects.

    GET → {states: {userId: "friend"|"incoming"|"outgoing"}, following: [userId]}
    (users with no relation are simply absent → the UI treats them as "suggested").
    POST ?do=request|accept|remove|follow|unfollow with {"user": <id>}.
    """
    permission_classes = [IsAuthenticated]

    def _tenant(self, request):
        return getattr(request, "tenant", None)

    def get(self, request):
        me = request.user
        states = {}
        qs = Friendship.objects.filter(Q(from_user=me) | Q(to_user=me))
        for f in qs:
            other = f.to_user_id if f.from_user_id == me.id else f.from_user_id
            if f.status == "accepted":
                states[str(other)] = "friend"
            elif f.from_user_id == me.id:
                states[str(other)] = "outgoing"
            else:
                states[str(other)] = "incoming"
        following = [str(x) for x in Follow.objects.filter(follower=me).values_list("followee_id", flat=True)]
        return Response({"states": states, "following": following})

    def post(self, request):
        me = request.user
        do = request.query_params.get("do")
        target_id = (request.data or {}).get("user")
        other = User.objects.filter(id=target_id).first()
        if not other or other.id == me.id:
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": "کاربر نامعتبر است."}}, status=422)
        tenant = self._tenant(request)

        if do == "request":
            Friendship.objects.get_or_create(
                from_user=me, to_user=other, defaults={"tenant": tenant, "status": "pending"})
            return Response({"state": "outgoing"})
        if do == "accept":
            f = Friendship.objects.filter(from_user=other, to_user=me).first()
            if f:
                f.status = "accepted"
                f.save(update_fields=["status"])
            return Response({"state": "friend"})
        if do == "remove":
            Friendship.objects.filter(
                Q(from_user=me, to_user=other) | Q(from_user=other, to_user=me)).delete()
            return Response({"state": "suggested"})
        if do == "follow":
            Follow.objects.get_or_create(follower=me, followee=other, defaults={"tenant": tenant})
            return Response({"following": True})
        if do == "unfollow":
            Follow.objects.filter(follower=me, followee=other).delete()
            return Response({"following": False})
        return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                   "message": "عملیات نامعتبر."}}, status=422)
