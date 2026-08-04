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

    image = models.CharField(max_length=120, blank=True, help_text="نام تصویر در public/img یا URL")

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

    image = models.CharField(max_length=120, blank=True, help_text="نام تصویر در public/img یا URL")

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

    image = models.CharField(max_length=120, blank=True, help_text="نام تصویر در public/img یا URL")

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

    image = models.CharField(max_length=120, blank=True, help_text="نام تصویر در public/img یا URL")

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


# ── نشریات سازمانی (ماهنامه بنیاد / نشریه بنیادتک) ──────────────────────────
class PublicationIssue(TenantScopedModel):
    MAGAZINES = [("bonyad", "ماهنامه بنیاد"), ("bonyadtech", "نشریه بنیادتک")]
    STAGES = [("collect", "گردآوری محتوا"), ("edit", "ویراستاری"), ("layout", "صفحه‌آرایی"),
              ("print", "چاپ و توزیع"), ("published", "منتشر شده")]
    magazine = models.CharField(max_length=12, choices=MAGAZINES, default="bonyad")
    issue_no = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=300)
    season = models.CharField(max_length=60, blank=True)
    stage = models.CharField(max_length=10, choices=STAGES, default="collect")
    articles = models.PositiveSmallIntegerField(default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_publication_issue"
        ordering = ["-issue_no"]

    def __str__(self):
        return f"{self.get_magazine_display()} — {self.issue_no}"


# ── سند فرصت‌های تحقیق و توسعه (تدوین سند برای هر شرکت) ─────────────────────
class RndDoc(TenantScopedModel):
    company = models.CharField(max_length=200)
    holding = models.CharField(max_length=200, blank=True)
    progress = models.PositiveSmallIntegerField(default=0, help_text="۰ تا ۱۰۰ روی ماشین وضعیت تدوین")
    status_label = models.CharField(max_length=200, blank=True)
    obstacles = models.CharField(max_length=300, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_rnd_doc"

    def __str__(self):
        return self.company


# ── شناسنامه‌ها: محصولات، واحدهای فناور، فناوران همکار ──────────────────────
class SupportedProduct(TenantScopedModel):
    name = models.CharField(max_length=300)
    company = models.CharField(max_length=200, blank=True)
    trl = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=200, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_supported_product"

    def __str__(self):
        return self.name


class SupportedVenture(TenantScopedModel):
    SUPPORT = [("tech_contract", "قرارداد فناورانه"), ("seed", "بذرمایه"), ("vc", "سرمایه خطرپذیر")]
    name = models.CharField(max_length=200)
    support_type = models.CharField(max_length=16, choices=SUPPORT, default="seed")
    field = models.CharField(max_length=120, blank=True)
    year = models.CharField(max_length=12, blank=True)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_supported_venture"

    def __str__(self):
        return self.name


class PartnerTechnologist(TenantScopedModel):
    name = models.CharField(max_length=200)
    expertise = models.CharField(max_length=200, blank=True)
    projects = models.PositiveSmallIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    class Meta(TenantScopedModel.Meta):
        db_table = "content_partner_technologist"

    def __str__(self):
        return self.name


class ContentComment(TenantScopedModel):
    """A comment on any content item (news/blog/event/media/knowledge/forum),
    referenced loosely by kind + object id so one model serves every showcase page."""
    KINDS = [("news", "خبر"), ("blog", "بلاگ"), ("event", "رویداد"),
             ("media", "رسانه"), ("doc", "سند"), ("forum", "تالار")]
    kind = models.CharField(max_length=8, choices=KINDS)
    object_id = models.UUIDField()
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="content_comments")
    body = models.TextField()
    accepted = models.BooleanField(default=False, help_text="پاسخ برگزیده")

    class Meta(TenantScopedModel.Meta):
        db_table = "content_comment"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["kind", "object_id"])]
