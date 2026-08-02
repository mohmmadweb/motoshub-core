from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.awards.models import AwardEntry
from apps.contracts.models import Contract
from apps.fund.models import Fund, NfProject
from apps.projects.models import Project
from apps.research.models import ResearchOpportunity
from apps.support.models import Ticket

from .models import WorkflowSettings
from .serializers import WorkflowSettingsSerializer


def _require(request, perm):
    user = request.user
    return user.is_superuser or perm in user.get_permission_ids(request.tenant)


class WorkflowSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings, _ = WorkflowSettings.objects.get_or_create(tenant=request.tenant)
        return Response(WorkflowSettingsSerializer(settings).data)

    def put(self, request):
        if not _require(request, "settings.security"):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        settings, _ = WorkflowSettings.objects.get_or_create(tenant=request.tenant)
        serializer = WorkflowSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReportSummaryView(APIView):
    """Aggregated counts across modules for the reports dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require(request, "reports.view"):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        t = request.tenant

        def by(qs, field):
            out = {}
            for row in qs.filter(tenant=t).values(field).order_by():
                out[row[field]] = out.get(row[field], 0) + 1
            return out

        return Response({
            "totals": {
                "projects": Project.objects.filter(tenant=t).count(),
                "contracts": Contract.objects.filter(tenant=t).count(),
                "funds": Fund.objects.filter(tenant=t).count(),
                "nf_projects": NfProject.objects.filter(tenant=t).count(),
                "tickets": Ticket.objects.filter(tenant=t).count(),
                "award_entries": AwardEntry.objects.filter(tenant=t).count(),
                "research": ResearchOpportunity.objects.filter(tenant=t).count(),
            },
            "projects_by_health": by(Project.objects, "health"),
            "contracts_by_stage": by(Contract.objects, "stage"),
            "funds_by_stage": by(Fund.objects, "stage"),
            "tickets_by_status": by(Ticket.objects, "status"),
            "research_by_stage": by(ResearchOpportunity.objects, "stage"),
        })


# ── Assistant (answers from LIVE data via a keyword intent matcher) ──────────
from apps.fund.models import NfPayment, NfReport  # noqa: E402


def _fa(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


SUGGESTIONS = [
    "چند پروژه فعال داریم؟",
    "سلامت پورتفولیو چگونه است؟",
    "چه گزارش‌هایی بررسی‌نشده مانده‌اند؟",
    "پرداخت‌های در جریان کدام‌اند؟",
    "قراردادهای در حال اجرا چندتاست؟",
    "وضعیت مسابقات و چالش‌ها چیست؟",
]


class AssistantView(APIView):
    """Persian Q&A grounded in live tenant data (keyword intent matcher)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"suggestions": SUGGESTIONS})

    def post(self, request):
        t = request.tenant
        q = (request.data or {}).get("question", "")

        def has(*words):
            return any(w in q for w in words)

        if has("پورتفولیو", "سلامت", "وضعیت پروژه"):
            by = {}
            for row in Project.objects.filter(tenant=t).values("health"):
                by[row["health"]] = by.get(row["health"], 0) + 1
            fa = {"green": "سبز", "yellow": "زرد", "red": "قرمز"}
            parts = "، ".join(f"{_fa(v)} {fa.get(k, k)}" for k, v in by.items()) or "بدون داده"
            return Response({"answer": f"سلامت پورتفولیو بر پایهٔ داده‌های زنده: {parts}."})
        if has("گزارش") and has("بررسی", "معوق", "مانده"):
            pending = NfReport.objects.filter(tenant=t, status__in=["under_review", "pending_upload", "needs_fix"]).count()
            return Response({"answer": f"در حال حاضر {_fa(pending)} گزارش در وضعیت بررسی/در انتظار است و نیازمند اقدام بررسی‌کننده می‌باشد."})
        if has("پرداخت"):
            await_ = NfPayment.objects.filter(tenant=t, status="await_order").count()
            paid = NfPayment.objects.filter(tenant=t, status="paid").count()
            return Response({"answer": f"{_fa(await_)} پرداخت در انتظار دستور پرداخت است و {_fa(paid)} پرداخت انجام شده."})
        if has("قرارداد"):
            executing = Contract.objects.filter(tenant=t, stage="executing").count()
            total = Contract.objects.filter(tenant=t).count()
            return Response({"answer": f"از مجموع {_fa(total)} قرارداد، {_fa(executing)} قرارداد در گام «در حال اجرا» است."})
        if has("مسابقه", "چالش"):
            from apps.competitions.models import Challenge, Competition
            return Response({"answer": f"{_fa(Competition.objects.filter(tenant=t).count())} مسابقه و {_fa(Challenge.objects.filter(tenant=t, status='active').count())} چالش فعال در جریان است."})
        if has("پروژه", "طرح", "صندوق", "چند"):
            projects = Project.objects.filter(tenant=t).count()
            nf = NfProject.objects.filter(tenant=t).count()
            return Response({"answer": f"{_fa(projects)} پروژه و {_fa(nf)} طرح صندوق نوآور در سامانه ثبت شده است. برای جزئیات هر طرح، شناسنامهٔ آن را در بخش صندوق نوآور ببینید."})
        return Response({"answer": "می‌توانم دربارهٔ شمار پروژه‌ها، سلامت پورتفولیو، گزارش‌های بررسی‌نشده، پرداخت‌های در جریان، قراردادها و مسابقات از داده‌های زندهٔ سامانه پاسخ دهم. لطفاً یکی از پرسش‌های پیشنهادی را انتخاب کنید یا پرسش را دقیق‌تر بیان کنید."})
