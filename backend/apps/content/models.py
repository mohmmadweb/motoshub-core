"""
Content modules: news, blog, events, media, knowledge.

All are tenant-scoped and carry the `Visibility` axis (public items surface on
the unauthenticated showcase). News additionally carries the `ContentScope` axis
(global / holding / company) for per-company publishing.
"""
from django.db import models

from apps.core.models import ContentScope, TenantScopedModel, Visibility


class News(TenantScopedModel):
    title = models.CharField(max_length=300)
    summary = models.CharField(max_length=500, blank=True)
    body = models.TextField(blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="news")
    pinned = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PRIVATE)

    # Scoped publishing (سراسری / هلدینگ / شرکت).
    scope = models.CharField(max_length=8, choices=ContentScope.choices, default=ContentScope.GLOBAL)
    holding = models.ForeignKey("tenancy.Holding", on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey("tenancy.Company", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_news"
        verbose_name_plural = "news"
        indexes = [models.Index(fields=["tenant", "pinned", "-created_at"])]

    def __str__(self):
        return self.title


class BlogPost(TenantScopedModel):
    title = models.CharField(max_length=300)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="blog_posts")
    excerpt = models.CharField(max_length=500, blank=True)
    body = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    tags = models.JSONField(default=list, blank=True)
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PRIVATE)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_blog_post"

    def __str__(self):
        return self.title


class EventMode(models.TextChoices):
    IN_PERSON = "in_person", "حضوری"
    ONLINE = "online", "آنلاین"


class Event(TenantScopedModel):
    title = models.CharField(max_length=300)
    starts_at = models.DateTimeField()
    location = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    attendees = models.PositiveIntegerField(default=0)
    hashtags = models.JSONField(default=list, blank=True)
    mode = models.CharField(max_length=10, choices=EventMode.choices, default=EventMode.IN_PERSON)
    join_link = models.URLField(blank=True)
    map_url = models.URLField(blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="events")
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PRIVATE)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_event"
        ordering = ["starts_at"]

    def __str__(self):
        return self.title


class MediaKind(models.TextChoices):
    PHOTO = "photo", "تصویر"
    VIDEO = "video", "ویدیو"


class MediaItem(TenantScopedModel):
    kind = models.CharField(max_length=6, choices=MediaKind.choices, default=MediaKind.PHOTO)
    title = models.CharField(max_length=300)
    album = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to="media/", blank=True, null=True)
    color = models.CharField(max_length=9, default="#1f4f99")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    tags = models.JSONField(default=list, blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="media")
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PRIVATE)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_media_item"

    def __str__(self):
        return self.title


class KnowledgeType(models.TextChoices):
    CONTRACT = "contract", "قرارداد"
    TRAINING = "training", "آموزشی"
    MINUTES = "minutes", "صورت‌جلسه"
    REPORT = "report", "گزارش"


class KnowledgeDoc(TenantScopedModel):
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=200, blank=True)
    doc_type = models.CharField(max_length=10, choices=KnowledgeType.choices, default=KnowledgeType.REPORT)
    file = models.FileField(upload_to="knowledge/", blank=True, null=True)
    size = models.CharField(max_length=32, blank=True)
    owner = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="knowledge_docs")
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PRIVATE)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_knowledge_doc"

    def __str__(self):
        return self.title
