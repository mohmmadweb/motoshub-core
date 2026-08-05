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


class Quiz(TenantScopedModel):
    """آزمون و داوری (iispors) — a timed assessment with a pass mark.

    Sits beside Poll because both are «سنجش» in the product: the Polls page is
    two tabs over the same idea. The question bank itself is out of scope here;
    what is tracked is the assessment's shape and each participant's result.
    """
    STATUS = [("open", "باز"), ("judging", "در حال داوری"), ("closed", "پایان‌یافته")]
    title = models.CharField(max_length=300)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="quizzes")
    questions = models.PositiveSmallIntegerField(default=0, help_text="تعداد سوال")
    minutes = models.PositiveSmallIntegerField(default=0, help_text="مدت به دقیقه")
    deadline = models.CharField(max_length=20, blank=True, help_text="مهلت (جلالی نمایشی)")
    status = models.CharField(max_length=8, choices=STATUS, default="open")
    passing = models.PositiveSmallIntegerField(default=60, help_text="حدنصاب قبولی (درصد)")

    class Meta(TenantScopedModel.Meta):
        db_table = "polls_quiz"

    def __str__(self):
        return self.title


class QuizAttempt(TenantScopedModel):
    """One participant's result. Unique per (quiz, user) — a score is a fact
    about a person's attempt, not a running log."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="quiz_attempts")
    score = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "polls_quiz_attempt"
        constraints = [models.UniqueConstraint(fields=["quiz", "user"], name="uniq_quiz_attempt")]
