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
from apps.contracts.models import Contract, ContractApproval, ContractPayment
from apps.fund.models import Fund, NfPayment, NfProject, NfReport, NfReportChainStep
from apps.awards.models import AwardEntry, AwardTrack
from apps.chat.models import Channel, Message
from apps.notifications.models import Notification
from apps.polls.models import Poll, PollOption
from apps.projects.models import Project, Task
from apps.research.models import ResearchOpportunity
from apps.rbac.models import Role, RoleAssignment
from apps.support.models import Ticket, TicketMessage
from apps.training.models import TrainingCourse
from apps.social.models import ForumReply, ForumTopic, Group, GroupMembership
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

        if not Group.objects.filter(tenant=tenant).exists():
            g_pub = Group.objects.create(
                tenant=tenant, owner=admin, name="گروه عمومی فناوری",
                description="بحث و تبادل نظر دربارهٔ فناوری‌های نوین.", privacy=Visibility.PUBLIC,
                color="#1f4f99", category="فناوری",
            )
            Group.objects.create(
                tenant=tenant, owner=admin, name="کارگروه راهبری بهنوش",
                description="گروه خصوصیِ مدیران شرکت بهنوش.", privacy=Visibility.PRIVATE,
                color="#b45309", category="مدیریت",
            )
            GroupMembership.objects.create(tenant=tenant, group=g_pub, user=admin, is_moderator=True)
            GroupMembership.objects.create(tenant=tenant, group=g_pub, user=member)

            topic = ForumTopic.objects.create(
                tenant=tenant, author=member, title="چگونه به سامانهٔ جدید مهاجرت کنیم؟",
                body="سوالی دربارهٔ فرآیند مهاجرت داشتم.", category="راهنما", views=42,
            )
            ForumReply.objects.create(tenant=tenant, topic=topic, author=admin, body="راهنمای کامل در بخش دانش موجود است.", is_solution=True)
            topic.solved = True
            topic.save(update_fields=["solved"])

        if not Project.objects.filter(tenant=tenant).exists():
            proj = Project.objects.create(
                tenant=tenant, manager=admin, author=admin, name="پیاده‌سازی سامانهٔ موتوشاب",
                client="بنیاد مستضعفان", health="yellow", progress=45, budget_total=800000000, budget_used=360000000,
            )
            Task.objects.create(tenant=tenant, project=proj, title="طراحی معماری بک‌اند", status="done", assignee=admin, priority="high", progress=100)
            Task.objects.create(tenant=tenant, project=proj, title="پیاده‌سازی احراز هویت", status="done", assignee=admin, priority="high", progress=100)
            Task.objects.create(tenant=tenant, project=proj, title="ماژول‌های محتوا", status="in_progress", assignee=member, priority="medium", progress=60)
            Task.objects.create(tenant=tenant, project=proj, title="فرانت‌اند Next", status="in_progress", assignee=admin, priority="high", progress=40)
            Task.objects.create(tenant=tenant, project=proj, title="آزمون پذیرش", status="planning", priority="medium", progress=0)

        if not Contract.objects.filter(tenant=tenant).exists():
            ct = Contract.objects.create(
                tenant=tenant, owner=admin, title="قرارداد پیاده‌سازی زیرساخت", vendor="شرکت فناوری سینا",
                stage="executing", contract_type="tech", method="public_call", value=500000000,
                guarantee="۱۰٪ حسن انجام کار",
            )
            ContractPayment.objects.create(tenant=tenant, contract=ct, title="پیش‌پرداخت", amount=125000000, status="paid")
            ContractPayment.objects.create(tenant=tenant, contract=ct, title="پرداخت مرحله‌ای اول", amount=200000000, status="pending")
            ContractApproval.objects.create(tenant=tenant, contract=ct, role="مدیر حقوقی", name="کارشناس حقوقی", status="approved", order=1)
            ContractApproval.objects.create(tenant=tenant, contract=ct, role="مدیر مالی", name="کارشناس مالی", status="pending", order=2)

        if not NfProject.objects.filter(tenant=tenant).exists():
            nf = NfProject.objects.create(
                tenant=tenant, fund_manager=admin, code="NF-1405-0001",
                title_fa="سامانهٔ هوشمند پایش انرژی", field="انرژی", rahbar="شرکت شتابدهی راهبر بنیاد",
                nazer="واحد فنی", budget=800000000, share_percent=40, duration_months=18,
                stage="monitoring", sub_status="بررسی گزارش مرحله‌ای", progress=55, screening_score=150, jury_score=72,
                team_name="تیم فناور پایش", team_type="تیم فناور", team_city="تهران",
            )
            rep = NfReport.objects.create(tenant=tenant, project=nf, report_type="stage", title="گزارش مرحله‌ای اول", status="under_review")
            NfReportChainStep.objects.create(tenant=tenant, report=rep, role="fund_manager", name="مدیر صندوق", status="approved", order=1)
            NfReportChainStep.objects.create(tenant=tenant, report=rep, role="nazer", name="ناظر فنی", status="pending", order=2)
            NfPayment.objects.create(tenant=tenant, project=nf, payment_type="prepayment", title="پیش‌پرداخت", amount=200000000, status="paid")
            NfPayment.objects.create(tenant=tenant, project=nf, payment_type="stage", title="پرداخت مرحله‌ای", amount=160000000, status="await_order")

        if not TrainingCourse.objects.filter(tenant=tenant).exists():
            TrainingCourse.objects.create(tenant=tenant, title="آشنایی با سامانهٔ موتوشاب", instructor="واحد آموزش", hours=8, capacity=40, status="open")
            TrainingCourse.objects.create(tenant=tenant, title="امنیت اطلاعات سازمانی", instructor="کارشناس امنیت", hours=12, capacity=25, status="running", satisfaction=4.6)

        if not Ticket.objects.filter(tenant=tenant).exists():
            tk = Ticket.objects.create(tenant=tenant, author=member, number="TK-10001", subject="عدم دسترسی به بخش گزارش‌ها", category="فنی", priority="urgent", status="answered")
            TicketMessage.objects.create(tenant=tenant, ticket=tk, author=member, body="هنگام ورود به گزارش‌ها خطا می‌گیرم.")
            TicketMessage.objects.create(tenant=tenant, ticket=tk, author=admin, from_support=True, body="دسترسی شما اصلاح شد؛ لطفاً دوباره تلاش کنید.")

        if not Poll.objects.filter(tenant=tenant).exists():
            poll = Poll.objects.create(tenant=tenant, author=admin, question="کدام قابلیت را زودتر می‌خواهید؟")
            for lbl in ["پیام‌رسان", "گزارش‌های پیشرفته", "اپ موبایل"]:
                PollOption.objects.create(tenant=tenant, poll=poll, label=lbl)

        if not ResearchOpportunity.objects.filter(tenant=tenant).exists():
            ResearchOpportunity.objects.create(tenant=tenant, author=admin, title="فراخوان پژوهشی هوش مصنوعی صنعتی", field="هوش مصنوعی", stage="review", budget=300000000, supervisor="دکتر نمونه")

        if not AwardTrack.objects.filter(tenant=tenant).exists():
            track = AwardTrack.objects.create(tenant=tenant, title="محور فناوری‌های نرم‌افزاری", categories=["هوش مصنوعی", "امنیت"])
            AwardEntry.objects.create(tenant=tenant, track=track, title="سامانهٔ پایش هوشمند", company="شرکت بهنوش", status="scored", score=88)
            AwardEntry.objects.create(tenant=tenant, track=track, title="پلتفرم تحلیل داده", company="زمزم", status="judging")

        if not Notification.objects.filter(tenant=tenant, user=admin).exists():
            Notification.objects.create(tenant=tenant, user=admin, text="گزارش مرحله‌ای طرح NF-1405-0001 در انتظار بررسی شماست.", kind="task")
            Notification.objects.create(tenant=tenant, user=admin, text="کاربر «کاربر نمونه» به گروه عمومی فناوری پیوست.", kind="system")

        if not Channel.objects.filter(tenant=tenant).exists():
            ch = Channel.objects.create(tenant=tenant, owner=admin, name="عمومی", topic="گفتگوی عمومی سازمان", channel_type="public", category="کانال‌ها")
            Message.objects.create(tenant=tenant, channel=ch, author=admin, text="به کانال عمومی موتوشاب خوش آمدید!")
            Message.objects.create(tenant=tenant, channel=ch, author=member, text="سلام، خوشحالم که این‌جا هستم.")
            Channel.objects.create(tenant=tenant, owner=admin, name="فناوری", topic="بحث‌های فنی", channel_type="public", category="کانال‌ها")

        if not Fund.objects.filter(tenant=tenant).exists():
            Fund.objects.create(tenant=tenant, title="طرح اشتغال‌زایی روستایی", applicant="تعاونی نمونه", stage="judging", amount=150000000, roi="۱۸٪")
            Fund.objects.create(tenant=tenant, title="حمایت از استارتاپ کشاورزی", applicant="شرکت سبز", stage="allocated", amount=300000000, roi="۲۴٪")

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
