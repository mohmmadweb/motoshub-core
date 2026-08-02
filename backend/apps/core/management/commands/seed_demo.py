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
from apps.contracts.models import (
    Contract,
    ContractApproval,
    ContractPayment,
    ESignDocument,
    ESignStep,
    TechTransferContract,
    Tender,
)
from apps.fund.models import Fund, NfGuarantee, NfPayment, NfProject, NfReport, NfReportChainStep, NfRequest
from apps.awards.models import AwardEntry, AwardTrack
from apps.chat.models import Channel, Message
from apps.notifications.models import Notification
from apps.polls.models import Poll, PollOption
from apps.projects.models import Project, Task
from apps.research.models import ResearchOpportunity
from apps.rbac.models import Role, RoleAssignment
from apps.support.models import Ticket, TicketMessage
from apps.training.models import TrainingCourse
from apps.social.models import Follow, ForumReply, ForumTopic, Friendship, Group, GroupMembership
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
