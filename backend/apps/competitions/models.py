"""Competitions (iiscompetition) + challenges (iischallenge)."""
from django.db import models

from apps.core.models import TenantScopedModel


class Competition(TenantScopedModel):
    STATUS = [("open", "ثبت‌نام باز"), ("judging", "در حال داوری"), ("results", "اعلام نتایج")]
    title = models.CharField(max_length=400)
    category = models.CharField(max_length=120, blank=True)
    deadline = models.CharField(max_length=20, blank=True, help_text="مهلت ارسال (جلالی نمایشی)")
    participants = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    prize = models.CharField(max_length=200, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "competitions_competition"

    def __str__(self):
        return self.title


class CompetitionEntry(TenantScopedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="entries")
    by = models.CharField(max_length=200)
    title = models.CharField(max_length=300)
    color = models.CharField(max_length=9, default="#5e7191")

    class Meta(TenantScopedModel.Meta):
        db_table = "competitions_entry"

    def __str__(self):
        return self.title


class EntryVote(TenantScopedModel):
    entry = models.ForeignKey(CompetitionEntry, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="entry_votes")

    class Meta(TenantScopedModel.Meta):
        db_table = "competitions_entry_vote"
        constraints = [models.UniqueConstraint(fields=["entry", "user"], name="uniq_entry_vote")]


class Challenge(TenantScopedModel):
    KIND = [("individual", "فردی"), ("collective", "همگانی")]
    STATUS = [("active", "فعال"), ("ended", "پایان‌یافته")]
    title = models.CharField(max_length=400)
    kind = models.CharField(max_length=12, choices=KIND, default="collective")
    category = models.CharField(max_length=120, blank=True)
    progress = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=STATUS, default="active")

    class Meta(TenantScopedModel.Meta):
        db_table = "competitions_challenge"

    def __str__(self):
        return self.title


class ChallengeMembership(TenantScopedModel):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="challenge_memberships")

    class Meta(TenantScopedModel.Meta):
        db_table = "competitions_challenge_member"
        constraints = [models.UniqueConstraint(fields=["challenge", "user"], name="uniq_challenge_member")]
