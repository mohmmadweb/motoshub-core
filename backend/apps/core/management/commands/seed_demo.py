"""
Seed a demo tenant with users, org tree, and sample content so the running stack
is testable end-to-end (login + browse). Idempotent: safe to run repeatedly.

Demo credentials (all password `demo1234`):
    admin   — org-admin (full access)
    member  — regular member (read/participate)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.content.models import BlogPost, Event, KnowledgeDoc, MediaItem, News
from apps.core.models import ContentScope, Visibility
from apps.rbac.models import Role, RoleAssignment
from apps.tenancy.models import Company, Holding, Tenant

PASSWORD = "demo1234"


class Command(BaseCommand):
    help = "Seed a demo tenant + users + sample content for live testing."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(
            domain="bonyad.shub.ir",
            defaults={"name": "بنیاد مستضعفان انقلاب اسلامی", "logo_color": "#1f4f99", "plan": "enterprise"},
        )
        holding, _ = Holding.objects.get_or_create(
            tenant=tenant, name="هلدینگ صنایع غذایی سینا", defaults={"color": "#b45309"}
        )
        company, _ = Company.objects.get_or_create(tenant=tenant, holding=holding, name="بهنوش ایران")

        admin = self._user("admin", "مدیر سیستم", tenant, company, "org-admin")
        member = self._user("member", "کاربر نمونه", tenant, company, "member")

        if not News.objects.filter(tenant=tenant).exists():
            News.objects.create(
                tenant=tenant, author=admin, title="افتتاح سامانهٔ جدید موتوشاب",
                summary="نسخهٔ جدید پلتفرم ارتباطات سازمانی راه‌اندازی شد.",
                visibility=Visibility.PUBLIC, scope=ContentScope.GLOBAL, pinned=True,
            )
            News.objects.create(
                tenant=tenant, author=admin, title="خبر ویژهٔ شرکت بهنوش",
                summary="این خبر فقط برای اعضای شرکت نمایش داده می‌شود.",
                visibility=Visibility.PRIVATE, scope=ContentScope.COMPANY, company=company,
            )
            BlogPost.objects.create(
                tenant=tenant, author=admin, title="یادداشت مدیرعامل",
                excerpt="نگاهی به مسیر پیشِ‌رو…", rating=5, tags=["راهبردی"], visibility=Visibility.PUBLIC,
            )
            Event.objects.create(
                tenant=tenant, author=admin, title="نشست فصلی مدیران",
                starts_at=timezone.now(), location="سالن همایش مرکزی", mode="in_person",
                visibility=Visibility.PUBLIC,
            )
            MediaItem.objects.create(
                tenant=tenant, author=admin, title="گالری بازدید هیأت مدیره",
                album="رویدادهای رسمی", kind="photo", visibility=Visibility.PUBLIC,
            )
            KnowledgeDoc.objects.create(
                tenant=tenant, owner=admin, title="آیین‌نامهٔ داخلی",
                category="حاکمیت", doc_type="report", size="۱٫۲ مگابایت", visibility=Visibility.PRIVATE,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Demo seeded: tenant «{tenant.name}» · users admin/member (pw {PASSWORD})"
        ))

    def _user(self, username, name, tenant, company, role_key):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"name": name, "tenant": tenant, "company": company},
        )
        if created:
            user.set_password(PASSWORD)
            user.save()
        role = Role.objects.filter(key=role_key, tenant__isnull=True).first()
        if role:
            RoleAssignment.objects.get_or_create(user=user, role=role, tenant=tenant)
        return user
