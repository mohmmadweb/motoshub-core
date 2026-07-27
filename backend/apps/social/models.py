"""
Social: groups (+ membership) and forum (topics + replies).

Privacy is enforced server-side: a private group's content is visible only to
members, its owner, or a `groups` moderator — never by guessing the id
(the IDOR lesson from the security audit).
"""
from django.db import models

from apps.core.models import TenantScopedModel, Visibility


class Group(TenantScopedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PUBLIC)
    color = models.CharField(max_length=9, default="#1f4f99")
    category = models.CharField(max_length=120, blank=True)
    owner = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="owned_groups")

    class Meta(TenantScopedModel.Meta):
        db_table = "social_group"

    def __str__(self):
        return self.name

    @property
    def member_count(self) -> int:
        return self.memberships.count()


class GroupMembership(TenantScopedModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="group_memberships")
    is_moderator = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "social_group_membership"
        constraints = [
            models.UniqueConstraint(fields=["group", "user"], name="uniq_group_member"),
        ]


class ForumTopic(TenantScopedModel):
    title = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="forum_topics")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="topics")
    category = models.CharField(max_length=120, blank=True)
    views = models.PositiveIntegerField(default=0)
    solved = models.BooleanField(default=False)
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta(TenantScopedModel.Meta):
        db_table = "social_forum_topic"

    def __str__(self):
        return self.title

    @property
    def reply_count(self) -> int:
        return self.replies.count()


class ForumReply(TenantScopedModel):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="forum_replies")
    body = models.TextField()
    is_solution = models.BooleanField(default=False)

    class Meta(TenantScopedModel.Meta):
        db_table = "social_forum_reply"
        ordering = ["created_at"]
