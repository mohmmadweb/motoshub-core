from django.db import models

from apps.core.models import TenantScopedModel


class Poll(TenantScopedModel):
    question = models.CharField(max_length=300)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="polls")
    ends_at = models.DateTimeField(null=True, blank=True)

    # A poll can belong to a group conversation (Telegram-style in-chat poll).
    group = models.ForeignKey("social.Group", on_delete=models.CASCADE, null=True, blank=True,
                              related_name="polls")

    class Meta(TenantScopedModel.Meta):
        db_table = "polls_poll"

    def __str__(self):
        return self.question


class PollOption(TenantScopedModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=200)

    class Meta(TenantScopedModel.Meta):
        db_table = "polls_option"
        ordering = ["created_at"]

    @property
    def votes(self) -> int:
        return self.ballots.count()


class PollVote(TenantScopedModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="ballots")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="poll_votes")

    class Meta(TenantScopedModel.Meta):
        db_table = "polls_vote"
        constraints = [models.UniqueConstraint(fields=["poll", "user"], name="uniq_vote_per_poll")]
