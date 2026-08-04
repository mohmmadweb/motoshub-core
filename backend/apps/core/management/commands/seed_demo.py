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
from apps.competitions.models import Challenge, Competition, CompetitionEntry
from apps.content.models import (PartnerTechnologist, PublicationIssue, RndDoc,
                                 SupportedProduct, SupportedVenture)
from apps.research.models import RfpCall, RfpVendor, Sabbatical, SabbaticalReport
from apps.contracts.models import (
    PendingReviewItem,
    ContractEvent,
    ContractObligation,
    Contract,
    ContractApproval,
    ContractPayment,
    ESignDocument,
    ESignStep,
    TechTransferContract,
    Tender,
)
from apps.fund.models import FundKpi, FundTranche, ReviewSession, Fund, NfGuarantee, NfPayment, NfProject, NfReport, NfReportChainStep, NfRequest
from apps.awards.models import AwardEntry, AwardTrack
from apps.chat.models import Channel, DirectMessage, Message
from apps.notifications.models import Notification
from apps.polls.models import Poll, PollOption
from apps.projects.models import (Milestone, PlaybookTemplate, Project, ProjectExpense,
                                  ProjectMember, ProjectMinute, Risk, Task)
from apps.research.models import ResearchOpportunity
from apps.rbac.models import Role, RoleAssignment
from apps.support.models import Ticket, TicketMessage
from apps.training.models import TrainingCourse
from apps.social.models import Follow, ForumReply, ForumTopic, Friendship, Group, GroupMembership, Post, PostLike
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
                client="بنیاد مستضعفان", department="اقتصادی و هلدینگ‌ها", health="yellow", progress=45, budget_total=800000000, budget_used=360000000,
            )
            Task.objects.create(tenant=tenant, project=proj, title="طراحی معماری بک‌اند", status="done", assignee=admin, priority="high", progress=100)
            Task.objects.create(tenant=tenant, project=proj, title="پیاده‌سازی احراز هویت", status="done", assignee=admin, priority="high", progress=100)
            Task.objects.create(tenant=tenant, project=proj, title="ماژول‌های محتوا", status="in_progress", assignee=member, priority="medium", progress=60)
            Task.objects.create(tenant=tenant, project=proj, title="فرانت‌اند Next", status="in_progress", assignee=admin, priority="high", progress=40)
            Task.objects.create(tenant=tenant, project=proj, title="آزمون پذیرش", status="planning", priority="medium", progress=0)
            # A couple more projects so the department/status charts have real spread.
            Project.objects.create(tenant=tenant, manager=admin, author=admin, name="طرح محرومیت‌زدایی سیستان",
                                   client="معاونت محرومیت‌زدایی", department="محرومیت‌زدایی", health="green",
                                   progress=70, budget_total=500000000, budget_used=300000000)
            Project.objects.create(tenant=tenant, manager=admin, author=admin, name="سامانهٔ فرهنگی نشر",
                                   client="معاونت فرهنگی", department="فرهنگی و اجتماعی", health="red",
                                   progress=20, budget_total=300000000, budget_used=90000000)
            for i, (mt, due, st) in enumerate([
                ("تحویل معماری و طرح فنی", "۱۴۰۴/۱۱/۳۰", "done"),
                ("راه‌اندازی نسخهٔ آزمایشی", "۱۴۰۵/۰۳/۱۵", "in_progress"),
                ("آزمون پذیرش کاربران", "۱۴۰۵/۰۶/۰۱", "upcoming"),
                ("استقرار نهایی و تحویل", "۱۴۰۵/۰۸/۳۰", "at_risk"),
            ]):
                Milestone.objects.create(tenant=tenant, project=proj, title=mt, due=due, status=st, order=i)
            Risk.objects.create(tenant=tenant, project=proj, title="تأخیر در تأمین زیرساخت ابری",
                                severity="critical", probability="medium", status="mitigating",
                                owner="مدیر فنی", mitigation="قرارداد پشتیبان با تأمین‌کنندهٔ دوم در حال مذاکره است.")
            Risk.objects.create(tenant=tenant, project=proj, title="کمبود نیروی متخصص فرانت‌اند",
                                severity="medium", probability="high", status="open",
                                owner="منابع انسانی", mitigation="آگهی جذب منتشر شد؛ همکاری پاره‌وقت در دست بررسی.")

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
                title_fa="سامانهٔ هوشمند پایش انرژی", title_en="Smart Energy Monitoring",
                field="انرژی", macro_field="اقتصاد دیجیتال و هوش مصنوعی",
                mother_project="رویداد راهی‌شو ۱۴۰۴", rahbar="شرکت شتابدهی راهبر بنیاد",
                nazer="واحد فنی", budget=800000000, share_percent=40, duration_months=18,
                contract_no="ق/۱۴۰۵/۰۰۱", stage="monitoring", sub_status="بررسی گزارش مرحله‌ای",
                green_path=False, progress=55, screening_score=150, jury_score=72,
                team_name="تیم فناور پایش", team_type="تیم فناور", team_city="تهران",
                team_manager="مهندس رستمی", team_members=6,
                finance={"prepayment": "۲۰۰٬۰۰۰٬۰۰۰ ریال", "approvedByProgress": "۴۴۰٬۰۰۰٬۰۰۰ ریال",
                         "paid": "۳۶۰٬۰۰۰٬۰۰۰ ریال", "pending": "۸۰٬۰۰۰٬۰۰۰ ریال",
                         "retention": "۳۶٬۰۰۰٬۰۰۰ ریال", "remaining": "۳۶۰٬۰۰۰٬۰۰۰ ریال"},
                gantt=[{"title": "تحلیل و طراحی", "weight": 20, "months": "۱–۳", "cost": "۱۶۰٬۰۰۰٬۰۰۰", "done": 100},
                       {"title": "پیاده‌سازی سنسورها", "weight": 40, "months": "۴–۹", "cost": "۳۲۰٬۰۰۰٬۰۰۰", "done": 70},
                       {"title": "یکپارچه‌سازی و تست", "weight": 25, "months": "۱۰–۱۴", "cost": "۲۰۰٬۰۰۰٬۰۰۰", "done": 20},
                       {"title": "بهره‌برداری آزمایشی", "weight": 15, "months": "۱۵–۱۸", "cost": "۱۲۰٬۰۰۰٬۰۰۰", "done": 0}],
                timeline=[{"date": "۱۴۰۴/۱۰/۰۱", "time": "۰۹:۳۰", "step": "تصویب طرح", "text": "طرح در کمیتهٔ سرمایه‌گذاری تصویب شد."},
                          {"date": "۱۴۰۴/۱۱/۱۵", "time": "۱۴:۰۰", "step": "تنظیم قرارداد", "text": "قرارداد سه‌جانبه امضا و پیش‌پرداخت صادر شد."},
                          {"date": "۱۴۰۵/۰۲/۲۰", "time": "۱۱:۱۵", "step": "نظارت و راهبری", "text": "گزارش مرحله‌ای اول بارگذاری شد؛ در حال بررسی ناظر."}],
            )
            NfGuarantee.objects.create(tenant=tenant, project=nf, kind="ضمانت‌نامه بانکی", amount=80000000, status="received")
            NfGuarantee.objects.create(tenant=tenant, project=nf, kind="سفتهٔ حسن انجام کار", amount=40000000, status="pending")
            rep = NfReport.objects.create(tenant=tenant, project=nf, report_type="stage", title="گزارش مرحله‌ای اول", status="under_review")
            NfReportChainStep.objects.create(tenant=tenant, report=rep, role="fund_manager", name="مدیر صندوق", status="approved", order=1)
            NfReportChainStep.objects.create(tenant=tenant, report=rep, role="nazer", name="ناظر فنی", status="pending", order=2)
            NfPayment.objects.create(tenant=tenant, project=nf, payment_type="پیش‌پرداخت", title="پیش‌پرداخت", amount=200000000, status="paid")
            NfPayment.objects.create(tenant=tenant, project=nf, payment_type="پرداخت مرحله‌ای", title="پرداخت مرحله‌ای", amount=160000000, status="await_order")
            NfRequest.objects.create(tenant=tenant, project=nf, request_type="extend", note="درخواست تمدید ددلاین میانی به دلیل تأخیر در واردات سنسور.", status="pending")

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

        # ── Rich contract sub-modules (tech-transfer / tender / e-sign) ──────────
        if not TechTransferContract.objects.filter(tenant=tenant).exists():
            tt = [
                ("تبادل فناوری", "پهپاد سمپاش کشاورزی — مزارع دشت ناز", "کارشناس ارشد کشاورزی و امنیت غذایی", "ساری", "فردوس پارس", "دشت ناز ساری", "شرکت فناور پرواز سبز", "بهره‌بردار و کارفرما", "ناظر و هماهنگ‌کننده", "۱۸ میلیارد ریال", "۹ میلیارد ریال (۵۰٪)", 70, 80, 55, "ضمانت‌نامه بانکی", ""),
                ("تبادل فناوری", "سامانه MOT چاه‌های نفت", "رییس بخش انرژی و نفت و گاز", "اهواز", "انرژی گستر سینا", "پدکس", "شرکت دانش‌بنیان ژرف‌کاو", "کارفرما", "هماهنگ‌کننده مالی", "۴۲ میلیارد ریال", "۲۱ میلیارد ریال (۵۰٪)", 45, 60, 40, "سفته", "صورت‌وضعیت ۲ در انتظار تایید ناظر"),
                ("تبادل فناوری", "انبارداری هوشمند مبتنی بر UWB", "رییس بخش اقتصاد دیجیتال", "تهران", "صنایع غذایی سینا", "بهنوش ایران", "تیم فناور ردیاب", "بهره‌بردار", "ناظر و هماهنگ‌کننده", "۱۲ میلیارد ریال", "۶ میلیارد ریال (۵۰٪)", 90, 95, 75, "چک", ""),
                ("تبادل فناوری", "تشخیص خودکار حوادث آزادراه تهران - شمال", "رییس بخش حمل‌ونقل ترکیبی", "تهران", "پایا ترابر سینا", "آزادراه تهران - شمال", "شرکت بینا رایان", "بهره‌بردار و کارفرما", "ناظر و هماهنگ‌کننده", "۲۵ میلیارد ریال", "۱۲.۵ میلیارد ریال (۵۰٪)", 100, 100, 85, "ضمانت‌نامه بانکی", "در انتظار آزادسازی حسن انجام کار"),
                ("تبادل فناوری", "لیدار پایش واگن‌های باری", "رییس بخش حمل‌ونقل ترکیبی", "اصفهان", "پایا ترابر سینا", "سینا ریل پارس", "شرکت فوتونیک آریا", "خریدار", "پیمانکار", "۹ میلیارد ریال", "۴.۵ میلیارد ریال (۵۰٪)", 30, 45, 25, "سفته", "تاخیر در واردات قطعات — درخواست الحاقیه زمانی"),
                ("تبادل فناوری", "کیت تشخیص سریع آنتی‌بیوتیک در شیر خام", "کارشناس ارشد امنیت غذایی", "تهران", "صنایع غذایی سینا", "لبنیات پاک", "شرکت زیست‌فناور کیمیا", "بهره‌بردار", "ناظر و هماهنگ‌کننده", "۷ میلیارد ریال", "۳.۵ میلیارد ریال (۵۰٪)", 60, 55, 50, "چک", ""),
                ("آموزشی-پژوهشی", "برنامه جامع آموزش هوش مصنوعی", "مجتبی سروش‌پور", "تهران", "ستاد بنیاد", "ایرانسل لبز", "موسسه آموزشی و پژوهشی سینا", "کارفرما", "طرف دوم", "۹۹ میلیارد ریال", "—", 40, 50, 35, "—", ""),
                ("تبادل فناوری", "کوره عملیات حرارتی قطعات نیروگاهی", "رییس بخش انرژی", "کرج", "برق و انرژی صبا", "نیروگاه‌های صبا", "شرکت مهندسی حرارت گستر", "کارفرما", "ناظر و هماهنگ‌کننده", "۳۱ میلیارد ریال", "۱۵.۵ میلیارد ریال (۵۰٪)", 15, 20, 20, "ضمانت‌نامه بانکی", "نیازمند استعلام از واحد مالی"),
            ]
            for k, ti, nz, ci, ho, co, mo, cr, dr, am, cm, pp, tp, fp, gu, no in tt:
                TechTransferContract.objects.create(
                    tenant=tenant, kind=k, title=ti, nazer=nz, city=ci, holding=ho, company=co,
                    mojri=mo, company_role=cr, daneshmand_role=dr, amount=am, commitment=cm,
                    physical_progress=pp, time_progress=tp, financial_progress=fp, guarantee=gu, note=no)

        if not Tender.objects.filter(tenant=tenant).exists():
            tn = [
                ("تجهیز آزمایشگاه مرکز نوآوری پارک پیامبر اعظم", "public", "commission", 6, "۱۴۰۵/۰۴/۲۵", "", "بازگشایی پاکات الف و ب انجام شد؛ پاکت ج در جلسه کمیسیون"),
                ("واگذاری فضای کار اشتراکی خانه خلاقیت علوی", "auction", "receive", 3, "", "", ""),
                ("خرید سرویس رایانش ابری پروژه‌های هوش مصنوعی", "no_formality", "contract", 1, "", "ابر آروان (نمونه)", "مصوبه ترک تشریفات هیئت مدیره پیوست است"),
                ("چاپ و توزیع شماره ۱۲ ماهنامه بنیاد", "limited", "award", 4, "", "چاپخانه اندیشه", ""),
            ]
            for ti, me, st, pa, sd, wi, no in tn:
                Tender.objects.create(tenant=tenant, title=ti, method=me, stage=st,
                                      participants=pa, session_date=sd, winner=wi, note=no)

        if not ESignDocument.objects.filter(tenant=tenant).exists():
            es = [
                ("قرارداد پروژه NF-1404-1051 — سامانه تشخیص نقص خط تولید زمزم", "nf", "NF-1404-1051", "",
                 [("مجری", "سیگنال امید", "awaiting", ""), ("راهبر", "شتابدهی تا ثریا", "queued", ""),
                  ("مدیرعامل موسسه", "صاحب امضا ۱", "queued", ""), ("عضو هیئت مدیره", "صاحب امضا ۲", "queued", "")]),
                ("قرارداد پروژه NF-1404-1053 — قطعات CFRP بدنه خودرو", "nf", "NF-1404-1053", "د/۱۴۰۴/۲۹۸۱",
                 [("مجری", "کربنیکس", "signed", "۱۴۰۴/۱۰/۲۲"), ("راهبر", "شتابدهی تا ثریا", "signed", "۱۴۰۴/۱۰/۲۳"),
                  ("مدیرعامل موسسه", "صاحب امضا ۱", "signed", "۱۴۰۴/۱۰/۲۴"), ("عضو هیئت مدیره", "صاحب امضا ۲", "signed", "۱۴۰۴/۱۰/۲۵")]),
                ("متمم زمانی قرارداد لیدار واگن‌های باری", "amendment", "سینا ریل پارس", "",
                 [("مجری", "فوتونیک آریا", "signed", "۱۴۰۵/۰۴/۰۱"), ("ناظر فنی", "رییس بخش حمل‌ونقل", "signed", "۱۴۰۵/۰۴/۰۲"),
                  ("مدیرعامل موسسه", "صاحب امضا ۱", "awaiting", ""), ("عضو هیئت مدیره", "صاحب امضا ۲", "queued", "")]),
            ]
            for ti, ki, rel, ln, steps in es:
                doc = ESignDocument.objects.create(tenant=tenant, title=ti, kind=ki, related_to=rel, letter_no=ln)
                for i, (ro, na, sta, da) in enumerate(steps):
                    ESignStep.objects.create(tenant=tenant, document=doc, role=ro, name=na, status=sta, date=da, order=i)

        # ── Direct messages (seed a couple of threads for admin) ─────────────────
        if not DirectMessage.objects.filter(tenant=tenant).exists() and member:
            DirectMessage.objects.create(tenant=tenant, sender=member, recipient=admin, text="سلام، وقت بخیر 🌱", read=True)
            DirectMessage.objects.create(tenant=tenant, sender=admin, recipient=member, text="سلام! بله بفرمایید.", read=True)
            DirectMessage.objects.create(tenant=tenant, sender=member, recipient=admin, text="گزارش این هفته را ارسال کردم، لطفاً بررسی بفرمایید.")

        # ── Competitions + challenges ────────────────────────────────────────────
        if not Competition.objects.filter(tenant=tenant).exists():
            cp1 = Competition.objects.create(
                tenant=tenant, title="مسابقه عکاسی «صنعت در قاب» — خطوط تولید شرکت‌های بنیاد",
                category="عکاسی", deadline="۱۴۰۵/۰۵/۲۰", participants=63, status="open",
                prize="۳ کمک‌هزینه سفر نمایشگاهی")
            for by, ti, col in [("دکتر آرین صدرا", "ربات جوشکار خط بدنه", "#5e7191"),
                                ("مهندس پارسا یگانه", "برداشت شبانه دشت ناز", "#0d9488"),
                                ("دکتر مهسا نیک‌اندیش", "آزمایشگاه کیت تشخیص", "#b45309")]:
                CompetitionEntry.objects.create(tenant=tenant, competition=cp1, by=by, title=ti, color=col)
            Competition.objects.create(
                tenant=tenant, title="مسابقه ایده «یک دقیقه برای بهره‌وری»",
                category="ویدیوی کوتاه", deadline="۱۴۰۵/۰۴/۲۵", participants=29, status="judging",
                prize="اعتبار آموزش تخصصی")

        if not Challenge.objects.filter(tenant=tenant).exists():
            Challenge.objects.create(tenant=tenant, title="چالش ۳۰ روز مستندسازی — هر روز یک درس‌آموخته در بانک دانش",
                                     kind="collective", category="مدیریت دانش", progress=40, status="active")
            Challenge.objects.create(tenant=tenant, title="چالش کاهش ۱۰٪ مصرف انرژی واحدها",
                                     kind="collective", category="انرژی", progress=65, status="active")
            Challenge.objects.create(tenant=tenant, title="چالش فردی: تکمیل پروفایل و مهارت‌ها",
                                     kind="individual", category="عمومی", progress=100, status="ended")


        # ── Activity feed posts ──────────────────────────────────────────────────
        if not Post.objects.filter(tenant=tenant).exists():
            grp = Group.objects.filter(tenant=tenant).first()
            p1 = Post.objects.create(
                tenant=tenant, author=admin, group=grp, pinned=True,
                content="سامانهٔ جدید موتوشاب راه‌اندازی شد. از امروز همهٔ فرآیندهای سازمانی — پروژه‌ها، قراردادها، صندوق نوآور و ارتباطات — در یک بستر واحد در دسترس است.",
                tags=["اطلاعیه", "موتوشاب"])
            p2 = Post.objects.create(
                tenant=tenant, author=member,
                content="گزارش مرحله‌ای طرح NF-1405-0001 بارگذاری شد و در انتظار بررسی ناظر فنی است.",
                tags=["صندوق نوآور"])
            Post.objects.create(
                tenant=tenant, author=admin, group=grp,
                content="نشست فصلی مدیران هفتهٔ آینده برگزار می‌شود؛ دستور جلسه در بخش رویدادها منتشر شد.",
                tags=["رویداد"], attachment={"type": "doc", "label": "دستور جلسهٔ نشست فصلی.pdf"})
            PostLike.objects.get_or_create(tenant=tenant, post=p1, user=member)
            PostLike.objects.get_or_create(tenant=tenant, post=p2, user=admin)



        # ── Project team / expenses / minutes / playbooks ────────────────────────
        first_project = Project.objects.filter(tenant=tenant).first()
        if first_project and not ProjectMember.objects.filter(tenant=tenant).exists():
            for nm, rl, al in [("محسن مردعلی", "مدیر پروژه", 80), ("وحید خاوئی", "کارشناس اشتغال و توانمندسازی", 60),
                               ("تیم عمرانی", "پیمانکار زیرساخت", 100), ("تیم آموزش", "تسهیل‌گری و آموزش", 40)]:
                ProjectMember.objects.create(tenant=tenant, project=first_project, name=nm, role=rl, allocation=al)
            for ti, ca, am, dt, st in [
                ("خرید لوله و اتصالات فاز اول", "زیرساخت", "۲٬۸۰۰٬۰۰۰٬۰۰۰ ریال", "۱۴۰۵/۰۱/۲۸", "paid"),
                ("دستمزد پیمانکار عمرانی — صورت‌وضعیت ۲", "پیمانکاری", "۱٬۹۰۰٬۰۰۰٬۰۰۰ ریال", "۱۴۰۵/۰۲/۲۰", "paid"),
                ("تجهیز کارگاه‌های اشتغال (چرخ خیاطی، ابزار)", "تجهیزات", "۱٬۲۰۰٬۰۰۰٬۰۰۰ ریال", "۱۴۰۵/۰۳/۰۵", "pending"),
                ("دوره تربیت تسهیل‌گران محلی", "آموزش", "۳۵۰٬۰۰۰٬۰۰۰ ریال", "۱۴۰۵/۰۳/۲۰", "planned"),
            ]:
                ProjectExpense.objects.create(tenant=tenant, project=first_project, title=ti, category=ca,
                                              amount=am, date=dt, status=st)
            for ti, dt, at, de, fu in [
                ("جلسه هماهنگی با فرمانداری قلعه‌گنج", "۱۴۰۵/۰۲/۰۸", 9, 4, 3),
                ("کمیته راهبری — پایش پیشرفت فاز دوم", "۱۴۰۵/۰۲/۲۲", 6, 3, 2),
            ]:
                ProjectMinute.objects.create(tenant=tenant, project=first_project, title=ti, date=dt,
                                             attendees=at, decisions=de, follow_ups=fu)
        if not PlaybookTemplate.objects.filter(tenant=tenant).exists():
            for nm, ca, st, uc in [
                ("واکنش به افزایش غیرعادی ترافیک", "عملیات/امنیت", 5, 3),
                ("فرآیند افتتاح و تحویل طرح عمرانی", "مدیریت پروژه", 6, 1),
                ("آماده‌سازی کارگاه آموزشی راهبران", "آموزش", 4, 2),
            ]:
                PlaybookTemplate.objects.create(tenant=tenant, name=nm, category=ca, steps=st, used_count=uc)

        # ── Contract obligations + history ───────────────────────────────────────
        first_contract = Contract.objects.filter(tenant=tenant).first()
        if first_contract and not ContractObligation.objects.filter(tenant=tenant).exists():
            for ti, du, dn in [("تحویل فاز اول زیرساخت", "۱۴۰۵/۰۲/۱۵", True),
                               ("ارائه گزارش پیشرفت ماهانه", "۱۴۰۵/۰۳/۰۱", True),
                               ("آموزش کاربران کلیدی", "۱۴۰۵/۰۴/۱۰", False),
                               ("تحویل مستندات فنی و کد منبع", "۱۴۰۵/۰۵/۳۰", False)]:
                ContractObligation.objects.create(tenant=tenant, contract=first_contract, title=ti, due=du, done=dn)
            for tx, dt in [("قرارداد ثبت و شماره‌گذاری شد", "۱۴۰۵/۰۱/۱۵"),
                           ("ضمانت‌نامه بانکی دریافت شد", "۱۴۰۵/۰۱/۲۰"),
                           ("پیش‌پرداخت پرداخت شد", "۱۴۰۵/۰۲/۰۱"),
                           ("صورت‌وضعیت ۱ تایید شد", "۱۴۰۵/۰۳/۰۵")]:
                ContractEvent.objects.create(tenant=tenant, contract=first_contract, text=tx, date=dt)

        if not PendingReviewItem.objects.filter(tenant=tenant).exists():
            for tp, ho, co, mo, ob, nt in [
                ("اتوماسیون انبار قطعات یدکی نیروگاه", "برق و انرژی صبا", "نیروگاه‌های صبا", "", "در انتظار تخصیص بودجه هلدینگ", ""),
                ("سامانه رزرو و فروش برخط هتل‌ها", "سیاحتی پارسیان", "هتل‌های پارسیان", "در حال انتخاب از فراخوان", "", "RFP در حال تدوین"),
                ("پایش کیفیت آب خروجی تصفیه‌خانه", "صنایع غذایی سینا", "زمزم ایران", "", "نیازمند تایید فنی", ""),
            ]:
                PendingReviewItem.objects.create(tenant=tenant, topic=tp, holding=ho, company=co,
                                                 mojri=mo, obstacles=ob, note=nt)

        # ── Fund dossier detail + review sessions ────────────────────────────────
        funds_qs = list(Fund.objects.filter(tenant=tenant))
        if funds_qs and not FundTranche.objects.filter(tenant=tenant).exists():
            f0 = funds_qs[0]
            f0.requested, f0.approved, f0.score = "۲۰۰٬۰۰۰٬۰۰۰ ریال", "۱۵۰٬۰۰۰٬۰۰۰ ریال", 82
            f0.committee, f0.region, f0.field = "کارگروه اشتغال روستایی", "کرمان — قلعه‌گنج", "کشاورزی و دامپروری"
            f0.notes = "طرح با اولویت اشتغال بانوان سرپرست خانوار تصویب شد."
            f0.save()
            for ti, am, cd, st in [("تخصیص اول (۵۰٪)", "۷۵٬۰۰۰٬۰۰۰ ریال", "پس از عقد قرارداد", "paid"),
                                   ("تخصیص دوم (۳۰٪)", "۴۵٬۰۰۰٬۰۰۰ ریال", "پس از گزارش پیشرفت ۵۰٪", "pending"),
                                   ("تخصیص نهایی (۲۰٪)", "۳۰٬۰۰۰٬۰۰۰ ریال", "پس از راه‌اندازی کامل", "conditional")]:
                FundTranche.objects.create(tenant=tenant, fund=f0, title=ti, amount=am, condition=cd, status=st)
            for lb, vl, tg, ok in [("اشتغال ایجادشده", "۱۴ نفر", "۲۰ نفر", True),
                                   ("درآمد ماهانه تعاونی", "۹۰ میلیون ریال", "۱۲۰ میلیون ریال", True),
                                   ("بازپرداخت تسهیلات", "۱۲٪", "۲۵٪", False)]:
                FundKpi.objects.create(tenant=tenant, fund=f0, label=lb, value=vl, target=tg, on_track=ok)
        if not ReviewSession.objects.filter(tenant=tenant).exists():
            ReviewSession.objects.create(tenant=tenant, title="جلسه داوری طرح‌های اشتغال خرد — نوبت ۱۴",
                                         date="۱۴۰۵/۰۴/۱۸", items=6, committee="کارگروه اشتغال روستایی")
            ReviewSession.objects.create(tenant=tenant, title="بررسی طرح‌های کشاورزی نیمه اول سال",
                                         date="۱۴۰۵/۰۴/۲۵", items=4, committee="کارگروه کشاورزی")

        # ── RFP (فراخوان فناور برتر) ─────────────────────────────────────────────
        if not RfpCall.objects.filter(tenant=tenant).exists():
            rfps = [
                ("RFP سامانه پایش برخط کیفیت شیر خام در زنجیره سرد", "لبنیات پاک", "صنایع غذایی سینا",
                 "selected", "۱۴۰۵/۰۲/۳۰", ["سامانه بنیاد", "سامانه ساخت داخل", "سامانه نان"],
                 [("زیست‌فناور کیمیا", 82, 88, True, "۹٬۸۰۰ میلیون ریال", True),
                  ("پایش‌گستر آزما", 74, 79, True, "۱۱٬۲۰۰ میلیون ریال", False),
                  ("تیم دانشگاهی صنعتی‌شریف", 68, 84, True, "۸٬۹۰۰ میلیون ریال", False)]),
                ("RFP هوشمندسازی توزین و بارگیری ناوگان ریلی", "سینا ریل پارس", "پایا ترابر سینا",
                 "tech", "۱۴۰۵/۰۵/۱۵", ["سامانه بنیاد", "سامانه جان"],
                 [("فوتونیک آریا", 78, None, False, "", False), ("رهاورد سنجش", 71, None, False, "", False),
                  ("مکاترونیک پیشرو", 64, None, False, "", False)]),
                ("RFP بازیافت حرارت کوره‌های عملیات حرارتی", "نیروگاه‌های صبا", "برق و انرژی صبا",
                 "docs", "۱۴۰۵/۰۶/۰۱", ["سامانه بنیاد", "سامانه ساخت داخل"],
                 [("حرارت گستر", None, None, False, "", False), ("ترمودینا", None, None, False, "", False)]),
            ]
            for ti, co, ho, st, dl, ch, vendors in rfps:
                call = RfpCall.objects.create(tenant=tenant, title=ti, company=co, holding=ho,
                                              stage=st, deadline=dl, channels=ch)
                for nm, bs, ts, po, pr, wn in vendors:
                    RfpVendor.objects.create(tenant=tenant, call=call, name=nm, biz_score=bs,
                                             tech_score=ts, price_opened=po, price=pr, winner=wn)

        # ── فرصت مطالعاتی اساتید ─────────────────────────────────────────────────
        if not Sabbatical.objects.filter(tenant=tenant).exists():
            sabs = [
                ("دکتر فرزانه توکلی", "دانشگاه صنعتی اصفهان", "صنایع غذایی سینا — بهنوش",
                 "کاهش ضایعات خط تولید نوشیدنی با تحلیل داده", 2, 4, "ف/۱۴۰۴/۰۸", "running",
                 [(1, "گزارش شناخت شرکت", "paid", "۲۵۰ میلیون ریال"),
                  (2, "گزارش ارائه راهکار", "sent", ""),
                  (3, "گزارش RFPهای پیشنهادی (حداقل ۶ عنوان: ۳ نوپا، ۲ R&D، ۱ کلان)", "pending", "")]),
                ("دکتر امیرحسین شعبانی", "دانشگاه تبریز", "کاوه پارس — زنجیره فولاد",
                 "کاهش مصرف انرژی در کوره‌های قوس الکتریکی", 3, None, "ف/۱۴۰۴/۱۱", "contract",
                 [(1, "گزارش شناخت شرکت", "pending", ""), (2, "گزارش ارائه راهکار", "pending", ""),
                  (3, "گزارش RFPهای پیشنهادی", "pending", "")]),
                ("دکتر لیلا قنبری", "دانشگاه فردوسی مشهد", "فردوس پارس — دشت ناز",
                 "الگوی آبیاری دقیق مبتنی بر سنجش از دور", 2, 5, "ف/۱۴۰۳/۲۱", "closed",
                 [(1, "گزارش شناخت شرکت", "paid", "۲۲۰ میلیون ریال"),
                  (2, "گزارش ارائه راهکار", "paid", "۲۸۰ میلیون ریال"),
                  (3, "گزارش RFPهای پیشنهادی (۷ عنوان)", "paid", "۳۰۰ میلیون ریال")]),
            ]
            for pr, un, ind, tp, tb, ta, ct, st, reports in sabs:
                sb = Sabbatical.objects.create(tenant=tenant, professor=pr, university=un, industry=ind,
                                               topic=tp, trl_before=tb, trl_after=ta, contract=ct, stage=st)
                for no, ti, stt, amt in reports:
                    SabbaticalReport.objects.create(tenant=tenant, sabbatical=sb, no=no, title=ti,
                                                    status=stt, paid_amount=amt)

        # ── نشریات ───────────────────────────────────────────────────────────────
        if not PublicationIssue.objects.filter(tenant=tenant).exists():
            for mag, no, ti, se, st, ar in [
                ("bonyad", 12, "ویژه‌نامه هوش مصنوعی در صنایع بنیاد", "تابستان ۱۴۰۵", "layout", 14),
                ("bonyad", 11, "زنجیره ارزش فولاد و فناوری‌های سبز", "بهار ۱۴۰۵", "published", 12),
                ("bonyadtech", 8, "گزارش رویداد راهی شو ۱۴۰۳ و تیم‌های برگزیده", "بهار ۱۴۰۵", "published", 9),
                ("bonyadtech", 9, "ویژه فراخوان‌های نیازهای فناورانه", "تابستان ۱۴۰۵", "collect", 5),
            ]:
                PublicationIssue.objects.create(tenant=tenant, magazine=mag, issue_no=no, title=ti,
                                                season=se, stage=st, articles=ar)

        # ── سندهای فرصت‌های تحقیق و توسعه ───────────────────────────────────────
        if not RndDoc.objects.filter(tenant=tenant).exists():
            for co, ho, pg, lb, ob in [
                ("دشت ناز ساری", "فردوس پارس", 100, "سند تدوین، تایید و تحویل شده", ""),
                ("بهنوش ایران", "صنایع غذایی سینا", 100, "سند تدوین، تایید و تحویل شده", ""),
                ("زمزم ایران", "صنایع غذایی سینا", 85, "پیش‌نویس نهایی در بررسی", ""),
                ("لبنیات پاک", "صنایع غذایی سینا", 65, "اصلاحات توسط تیم راهبر", ""),
                ("سینا ریل پارس", "پایا ترابر سینا", 45, "ویرایش اول ارائه شده", ""),
                ("آزادراه تهران - شمال", "پایا ترابر سینا", 100, "سند تدوین، تایید و تحویل شده", ""),
                ("بانک سینا", "مالی و سرمایه‌گذاری سینا", 20, "عناوین احصاء شده — در بررسی", "در انتظار تعیین نماینده تحول دیجیتال"),
                ("بیمه سینا", "مالی و سرمایه‌گذاری سینا", 10, "بازدید و احصاء عناوین", ""),
                ("نیروگاه‌های صبا", "برق و انرژی صبا", 45, "ویرایش اول ارائه شده", ""),
                ("انرژی گستر سینا", "برق و انرژی صبا", 65, "اصلاحات توسط تیم راهبر", "نیاز به جلسه تکمیلی با معاونت بهره‌برداری"),
                ("کاوه پارس (فولاد)", "کاوه پارس", 20, "عناوین احصاء شده — در بررسی", ""),
                ("هتل‌های پارسیان", "سیاحتی پارسیان", 10, "بازدید و احصاء عناوین", ""),
            ]:
                RndDoc.objects.create(tenant=tenant, company=co, holding=ho, progress=pg,
                                      status_label=lb, obstacles=ob)

        # ── شناسنامه‌ها ─────────────────────────────────────────────────────────
        if not SupportedProduct.objects.filter(tenant=tenant).exists():
            for nm, co, trl, st in [
                ("کیت تشخیص سریع آنتی‌بیوتیک شیر", "زیست‌فناور کیمیا", 7, "در حال استقرار در لبنیات پاک"),
                ("سامانه تشخیص خودکار حوادث جاده‌ای", "بینا رایان", 9, "بهره‌برداری تجاری"),
                ("پهپاد سمپاش ۲۰ لیتری", "پرواز سبز", 8, "پایلوت مزارع دشت ناز"),
                ("خمیرکاغذ کرافت ارگانوسولو", "اکال زیست پایدار", 4, "پروتوتایپ در صندوق نوآور"),
            ]:
                SupportedProduct.objects.create(tenant=tenant, name=nm, company=co, trl=trl, status=st)
            for nm, sp, fl, yr in [
                ("اکال زیست پایدار", "tech_contract", "زیست‌فناوری", "۱۴۰۴"),
                ("زیست‌پالا", "seed", "محیط زیست", "۱۴۰۴"),
                ("رهیاب‌انرژی", "seed", "انرژی", "۱۴۰۳"),
                ("بینا رایان", "vc", "بینایی ماشین", "۱۴۰۲"),
                ("سیگنال امید", "tech_contract", "هوش مصنوعی", "۱۴۰۴"),
            ]:
                SupportedVenture.objects.create(tenant=tenant, name=nm, support_type=sp, field=fl, year=yr)
            for nm, ex, pj, rt in [
                ("شرکت شتابدهی و فناوری راهبر بنیاد", "راهبری و شتابدهی تیم‌ها", 5, 4.6),
                ("زیست‌فناور کیمیا", "کیت‌های تشخیصی", 2, 4.4),
                ("فوتونیک آریا", "لیدار و سنجش نوری", 1, 4.0),
                ("پرواز سبز", "پهپاد کشاورزی", 1, 4.5),
            ]:
                PartnerTechnologist.objects.create(tenant=tenant, name=nm, expertise=ex, projects=pj, rating=rt)

        # ── Social graph: colleagues + friends + follows (Friends/Profile pages) ──
        colleagues = [
            ("m.rezaei", "محمد رضایی", "رئیس بنیاد", "#0d9488", ["راهبری کلان", "سیاست‌گذاری"], "online"),
            ("f.karimi", "فاطمه کریمی", "معاون فناوری", "#b45309", ["نوآوری", "تحول دیجیتال"], "online"),
            ("a.hoseini", "علی حسینی", "مدیر پروژه", "#7c3aed", ["مدیریت پروژه", "اجایل"], "away"),
            ("z.ahmadi", "زهرا احمدی", "کارشناس محتوا", "#be185d", ["تولید محتوا", "سئو"], "offline"),
            ("h.moradi", "حسن مرادی", "مدیر مالی", "#1d4ed8", ["حسابداری", "بودجه‌ریزی"], "online"),
            ("s.jafari", "سمیرا جعفری", "کارشناس منابع انسانی", "#059669", ["جذب", "آموزش"], "offline"),
            ("r.gholami", "رضا غلامی", "توسعه‌دهنده ارشد", "#ea580c", ["بک‌اند", "معماری"], "dnd"),
            ("n.sadeghi", "نرگس صادقی", "طراح تجربه کاربری", "#0891b2", ["UI/UX", "پژوهش کاربر"], "online"),
        ]
        people = [self._user(un, nm, tenant, company, "member", title=ti,
                             avatar_color=col, skills=sk, presence=pr)
                  for un, nm, ti, col, sk, pr in colleagues]
        if not Friendship.objects.filter(from_user=admin).exists() and people:
            for u in people[:3]:
                Friendship.objects.get_or_create(from_user=admin, to_user=u, defaults={"tenant": tenant, "status": "accepted"})
            for u in people[3:5]:
                Friendship.objects.get_or_create(from_user=u, to_user=admin, defaults={"tenant": tenant, "status": "pending"})
            for u in people[5:6]:
                Friendship.objects.get_or_create(from_user=admin, to_user=u, defaults={"tenant": tenant, "status": "pending"})
            for u in people[:2]:
                Follow.objects.get_or_create(follower=admin, followee=u, defaults={"tenant": tenant})

        self.stdout.write(self.style.SUCCESS(
            f"Demo seeded: tenant «{tenant.name}» · users admin/member (pw {PASSWORD})"
        ))

    def _user(self, username, name, tenant, company, role_key, **profile):
        defaults = {"name": name, "tenant": tenant, "company": company,
                    "org": tenant.name if tenant else "", **profile}
        user, created = User.objects.get_or_create(username=username, defaults=defaults)
        if created:
            user.set_password(PASSWORD)
            user.save()
        role = Role.objects.filter(key=role_key, tenant__isnull=True).first()
        if role:
            RoleAssignment.objects.get_or_create(user=user, role=role, tenant=tenant)
        return user
