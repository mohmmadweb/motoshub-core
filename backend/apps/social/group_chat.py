"""
Group conversations — a Telegram-grade group chat.

A group's conversation is a `chat.Channel` bound one-to-one to the group, so the
whole chat stack (messages, reactions, pins, realtime WebSocket) is reused rather
than duplicated. Everything here is about *group* semantics: roles, moderation,
invites, slow mode, mute and read state.
"""
import secrets
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models import Channel, Message
from apps.chat.serializers import MessageSerializer

from .models import Group, GroupMembership


def channel_for(group: Group) -> Channel:
    """The group's conversation channel, created on first use."""
    channel = getattr(group, "channel", None)
    if channel is None:
        channel = Channel.objects.create(
            tenant=group.tenant, group=group, name=group.name,
            topic=group.description[:300], channel_type=group.privacy,
            category="گروه‌ها", owner=group.owner,
        )
    return channel


def _broadcast(group: Group, payload: dict, event: str = "chat.message"):
    layer = get_channel_layer()
    if layer is not None:
        async_to_sync(layer.group_send)(f"chat_{channel_for(group).id}", {"type": event, "message": payload})


class GroupAccess:
    """Resolves the caller's membership and what they're allowed to do."""

    def __init__(self, request, group_id):
        self.request = request
        self.group = Group.objects.filter(id=group_id, tenant=request.tenant).first()
        self.membership = (
            GroupMembership.objects.filter(group=self.group, user=request.user).first()
            if self.group else None
        )

    @property
    def is_owner(self):
        return bool(self.group and self.group.owner_id == self.request.user.id)

    @property
    def can_moderate(self):
        return self.is_owner or bool(self.membership and self.membership.can_moderate) \
            or self.request.user.is_superuser

    @property
    def can_read(self):
        """Private groups are members-only; public ones are readable tenant-wide."""
        if not self.group:
            return False
        if self.membership and self.membership.banned:
            return False
        return self.group.privacy == "public" or self.membership is not None or self.can_moderate

    @property
    def can_post(self):
        return bool(self.membership and not self.membership.banned) or self.can_moderate


def _deny(msg, code=403):
    return Response({"error": {"code": code, "type": "forbidden" if code == 403 else "not_found",
                               "message": msg}}, status=code)


class GroupMessagesView(APIView):
    """GET the conversation · POST a message (reply / forward / attachment)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_read:
            return _deny("این گروه خصوصی است.")
        qs = Message.objects.filter(channel=channel_for(acc.group)) \
            .select_related("author", "reply_to__author").prefetch_related("reactions")[:300]
        data = MessageSerializer(qs, many=True, context={"request": request}).data
        # Mark the conversation read for this member.
        if acc.membership:
            acc.membership.last_read_at = timezone.now()
            acc.membership.save(update_fields=["last_read_at"])
        return Response(data)

    def post(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_post:
            return _deny("برای ارسال پیام باید عضو گروه باشید.")
        body = request.data or {}
        text = (body.get("text") or "").strip()
        attachment = body.get("attachment")
        if not text and not attachment:
            return _deny("متن پیام الزامی است.", 422)

        # Slow mode: members (not moderators) must wait between messages.
        m = acc.membership
        if m and acc.group.slow_mode_seconds and not acc.can_moderate and m.last_message_at:
            waited = (timezone.now() - m.last_message_at).total_seconds()
            if waited < acc.group.slow_mode_seconds:
                left = int(acc.group.slow_mode_seconds - waited)
                return _deny(f"حالت آهسته فعال است — {left} ثانیه دیگر می‌توانید پیام بفرستید.", 429)

        reply_to = None
        if body.get("reply_to_id"):
            reply_to = Message.objects.filter(id=body["reply_to_id"], channel=channel_for(acc.group)).first()

        msg = Message.objects.create(
            tenant=request.tenant, channel=channel_for(acc.group), author=request.user,
            text=text, reply_to=reply_to, forwarded_from=(body.get("forwarded_from") or "")[:200],
            attachment=attachment or None, mentions=body.get("mentions") or [],
        )
        if m:
            m.last_message_at = timezone.now()
            m.save(update_fields=["last_message_at"])
        data = MessageSerializer(msg, context={"request": request}).data
        _broadcast(acc.group, data)
        return Response(data, status=201)


class GroupMessageDetailView(APIView):
    """Edit / delete / pin a single message (author or moderator)."""
    permission_classes = [IsAuthenticated]

    def _msg(self, acc, message_id):
        return Message.objects.filter(id=message_id, channel=channel_for(acc.group)).first()

    def patch(self, request, group_id=None, message_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        msg = self._msg(acc, message_id)
        if not msg:
            return _deny("پیام یافت نشد.", 404)
        body = request.data or {}

        if "pinned" in body:                       # pin/unpin — moderators only
            if not acc.can_moderate:
                return _deny("سنجاق‌کردن پیام فقط توسط مدیران گروه ممکن است.")
            msg.pinned = bool(body["pinned"])
            msg.save(update_fields=["pinned"])
        if "text" in body:                         # edit — author only
            if msg.author_id != request.user.id:
                return _deny("فقط نویسندهٔ پیام می‌تواند آن را ویرایش کند.")
            if msg.deleted:
                return _deny("پیام حذف‌شده قابل ویرایش نیست.", 422)
            msg.text = (body["text"] or "").strip()
            msg.edited_at = timezone.now()
            msg.save(update_fields=["text", "edited_at"])

        data = MessageSerializer(msg, context={"request": request}).data
        _broadcast(acc.group, data)
        return Response(data)

    def delete(self, request, group_id=None, message_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        msg = self._msg(acc, message_id)
        if not msg:
            return _deny("پیام یافت نشد.", 404)
        if msg.author_id != request.user.id and not acc.can_moderate:
            return _deny("فقط نویسنده یا مدیر گروه می‌تواند پیام را حذف کند.")
        msg.deleted, msg.pinned = True, False
        msg.save(update_fields=["deleted", "pinned"])
        _broadcast(acc.group, MessageSerializer(msg, context={"request": request}).data)
        return Response(status=204)


class GroupMembersView(APIView):
    """List members · add a member (moderators)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_read:
            return _deny("این گروه خصوصی است.")
        from .serializers import GroupMemberSerializer
        rows = GroupMembership.objects.filter(group=acc.group).select_related("user")
        return Response(GroupMemberSerializer(rows, many=True, context={"request": request}).data)

    def post(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_moderate:
            return _deny("افزودن عضو فقط توسط مدیران گروه ممکن است.")
        from apps.accounts.models import User
        from .serializers import GroupMemberSerializer
        user = User.objects.filter(id=(request.data or {}).get("user_id"), tenant=request.tenant).first()
        if not user:
            return _deny("کاربر یافت نشد.", 422)
        row, _ = GroupMembership.objects.get_or_create(
            group=acc.group, user=user, defaults={"tenant": request.tenant, "role": "member"})
        return Response(GroupMemberSerializer(row, context={"request": request}).data, status=201)


class GroupMemberDetailView(APIView):
    """Promote / demote / mute / ban / remove a member."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, group_id=None, user_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        row = GroupMembership.objects.filter(group=acc.group, user_id=user_id).first()
        if not row:
            return _deny("عضو یافت نشد.", 404)
        body = request.data or {}
        me_is_target = str(user_id) == str(request.user.id)

        # A member may only silence their own notifications.
        if set(body) - {"muted"} and not acc.can_moderate:
            return _deny("تغییر نقش یا وضعیت اعضا فقط توسط مدیران گروه ممکن است.")
        if "muted" in body and (me_is_target or acc.can_moderate):
            row.muted = bool(body["muted"])
        if "role" in body and acc.can_moderate:
            if row.user_id == acc.group.owner_id:
                return _deny("نقش مالک گروه قابل تغییر نیست.", 422)
            if body["role"] not in {"admin", "member"}:
                return _deny("نقش نامعتبر است.", 422)
            row.role = body["role"]
            row.is_moderator = row.role == "admin"
        if "banned" in body and acc.can_moderate:
            if row.user_id == acc.group.owner_id:
                return _deny("مالک گروه قابل محدودسازی نیست.", 422)
            row.banned = bool(body["banned"])
        row.save()
        from .serializers import GroupMemberSerializer
        return Response(GroupMemberSerializer(row, context={"request": request}).data)

    def delete(self, request, group_id=None, user_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        me_is_target = str(user_id) == str(request.user.id)
        if not (me_is_target or acc.can_moderate):
            return _deny("حذف عضو فقط توسط مدیران گروه ممکن است.")
        if str(user_id) == str(acc.group.owner_id):
            return _deny("مالک گروه قابل حذف نیست.", 422)
        GroupMembership.objects.filter(group=acc.group, user_id=user_id).delete()
        return Response(status=204)


class GroupInviteView(APIView):
    """Read or rotate the group's invite link (moderators) · join by code."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_moderate:
            return _deny("لینک دعوت فقط برای مدیران گروه قابل مشاهده است.")
        if not acc.group.invite_code:
            acc.group.invite_code = secrets.token_urlsafe(9)
            acc.group.save(update_fields=["invite_code"])
        return Response({"invite_code": acc.group.invite_code})

    def post(self, request, group_id=None):
        """Rotate — invalidates the previous link."""
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_moderate:
            return _deny("چرخش لینک دعوت فقط توسط مدیران گروه ممکن است.")
        acc.group.invite_code = secrets.token_urlsafe(9)
        acc.group.save(update_fields=["invite_code"])
        return Response({"invite_code": acc.group.invite_code})


class GroupJoinByInviteView(APIView):
    """Join a group with an invite code (works for private groups)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = (request.data or {}).get("invite_code", "")
        group = Group.objects.filter(invite_code=code, tenant=request.tenant).first() if code else None
        if not group:
            return _deny("لینک دعوت نامعتبر یا منقضی است.", 404)
        row = GroupMembership.objects.filter(group=group, user=request.user).first()
        if row and row.banned:
            return _deny("شما از این گروه محدود شده‌اید.")
        GroupMembership.objects.get_or_create(
            group=group, user=request.user, defaults={"tenant": request.tenant, "role": "member"})
        return Response({"group_id": str(group.id), "name": group.name}, status=201)


class GroupSettingsView(APIView):
    """Group-level settings a moderator can change (slow mode, privacy, info)."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group:
            return _deny("گروه یافت نشد.", 404)
        if not acc.can_moderate:
            return _deny("تغییر تنظیمات فقط توسط مدیران گروه ممکن است.")
        body = request.data or {}
        changed = []
        for field in ("name", "description", "privacy", "color", "category"):
            if field in body:
                setattr(acc.group, field, body[field])
                changed.append(field)
        if "slow_mode_seconds" in body:
            acc.group.slow_mode_seconds = max(0, int(body["slow_mode_seconds"] or 0))
            changed.append("slow_mode_seconds")
        if changed:
            acc.group.save(update_fields=changed)
        from .serializers import GroupSerializer
        return Response(GroupSerializer(acc.group, context={"request": request}).data)


class GroupTypingView(APIView):
    """Broadcast a typing indicator to the group's live subscribers."""
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id=None):
        acc = GroupAccess(request, group_id)
        if not acc.group or not acc.can_post:
            return Response(status=204)
        _broadcast(acc.group, {"user": request.user.name, "user_id": str(request.user.id)},
                   event="chat.typing")
        return Response(status=204)
