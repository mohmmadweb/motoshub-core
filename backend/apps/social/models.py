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


class Friendship(TenantScopedModel):
    """A directed friend request that becomes symmetric once accepted.

    `from_user` initiated it. status=pending → an outgoing request for from_user
    and an incoming one for to_user; status=accepted → the two are friends.
    """
    STATUS = [("pending", "در انتظار"), ("accepted", "دوست")]
    from_user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="friendships_sent")
    to_user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="friendships_received")
    status = models.CharField(max_length=10, choices=STATUS, default="pending")

    class Meta(TenantScopedModel.Meta):
        db_table = "social_friendship"
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="uniq_friendship_pair"),
        ]


class Follow(TenantScopedModel):
    follower = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="following_set")
    followee = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="follower_set")

    class Meta(TenantScopedModel.Meta):
        db_table = "social_follow"
        constraints = [
            models.UniqueConstraint(fields=["follower", "followee"], name="uniq_follow_pair"),
        ]


class Post(TenantScopedModel):
    """Feed post (dashboard/profile/groups) — the social activity stream."""
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    pinned = models.BooleanField(default=False)
    attachment = models.JSONField(null=True, blank=True)  # {type: poll|image|doc, label}

    class Meta(TenantScopedModel.Meta):
        db_table = "social_post"
        ordering = ["-pinned", "-created_at"]

    def __str__(self):
        return self.content[:40]


class PostLike(TenantScopedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="post_likes")

    class Meta(TenantScopedModel.Meta):
        db_table = "social_post_like"
        constraints = [models.UniqueConstraint(fields=["post", "user"], name="uniq_post_like")]


class PostComment(TenantScopedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="post_comments")
    body = models.TextField()

    class Meta(TenantScopedModel.Meta):
        db_table = "social_post_comment"
        ordering = ["created_at"]
