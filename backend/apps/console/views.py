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


def _rule_answer(t, q):
    """Deterministic keyword matcher over live tenant data. Always available."""
    def has(*words):
        return any(w in q for w in words)

    if has("پورتفولیو", "سلامت", "وضعیت پروژه"):
        by = {}
        for row in Project.objects.filter(tenant=t).values("health"):
            by[row["health"]] = by.get(row["health"], 0) + 1
        fa = {"green": "سبز", "yellow": "زرد", "red": "قرمز"}
        parts = "، ".join(f"{_fa(v)} {fa.get(k, k)}" for k, v in by.items()) or "بدون داده"
        return f"سلامت پورتفولیو بر پایهٔ داده‌های زنده: {parts}."
    if has("گزارش") and has("بررسی", "معوق", "مانده"):
        pending = NfReport.objects.filter(tenant=t, status__in=["under_review", "pending_upload", "needs_fix"]).count()
        return f"در حال حاضر {_fa(pending)} گزارش در وضعیت بررسی/در انتظار است و نیازمند اقدام بررسی‌کننده می‌باشد."
    if has("پرداخت"):
        await_ = NfPayment.objects.filter(tenant=t, status="await_order").count()
        paid = NfPayment.objects.filter(tenant=t, status="paid").count()
        return f"{_fa(await_)} پرداخت در انتظار دستور پرداخت است و {_fa(paid)} پرداخت انجام شده."
    if has("قرارداد"):
        executing = Contract.objects.filter(tenant=t, stage="executing").count()
        total = Contract.objects.filter(tenant=t).count()
        return f"از مجموع {_fa(total)} قرارداد، {_fa(executing)} قرارداد در گام «در حال اجرا» است."
    if has("مسابقه", "چالش"):
        from apps.competitions.models import Challenge, Competition
        return f"{_fa(Competition.objects.filter(tenant=t).count())} مسابقه و {_fa(Challenge.objects.filter(tenant=t, status='active').count())} چالش فعال در جریان است."
    if has("پروژه", "طرح", "صندوق", "چند"):
        return (f"{_fa(Project.objects.filter(tenant=t).count())} پروژه و "
                f"{_fa(NfProject.objects.filter(tenant=t).count())} طرح صندوق نوآور در سامانه ثبت شده است. "
                "برای جزئیات هر طرح، شناسنامهٔ آن را در بخش صندوق نوآور ببینید.")
    return ("می‌توانم دربارهٔ شمار پروژه‌ها، سلامت پورتفولیو، گزارش‌های بررسی‌نشده، پرداخت‌های در جریان، "
            "قراردادها و مسابقات از داده‌های زندهٔ سامانه پاسخ دهم. لطفاً یکی از پرسش‌های پیشنهادی را انتخاب کنید.")


def _live_context(t):
    """Compact real-data snapshot handed to the LLM so its answers stay grounded."""
    from apps.competitions.models import Challenge, Competition
    health = {}
    for row in Project.objects.filter(tenant=t).values("health"):
        health[row["health"]] = health.get(row["health"], 0) + 1
    return (
        "دادهٔ زندهٔ سامانه (این تنها منبع موثقِ توست):\n"
        f"- پروژه‌ها: {Project.objects.filter(tenant=t).count()} (سلامت: {health or 'نامشخص'})\n"
        f"- طرح‌های صندوق نوآور: {NfProject.objects.filter(tenant=t).count()}\n"
        f"- قراردادها: کل {Contract.objects.filter(tenant=t).count()}، در حال اجرا {Contract.objects.filter(tenant=t, stage='executing').count()}\n"
        f"- گزارش‌های در انتظار/در حال بررسی: {NfReport.objects.filter(tenant=t, status__in=['under_review','pending_upload','needs_fix']).count()}\n"
        f"- پرداخت‌ها: در انتظار دستور {NfPayment.objects.filter(tenant=t, status='await_order').count()}، انجام‌شده {NfPayment.objects.filter(tenant=t, status='paid').count()}\n"
        f"- تیکت‌ها: {Ticket.objects.filter(tenant=t).count()}\n"
        f"- مسابقات: {Competition.objects.filter(tenant=t).count()}، چالش‌های فعال: {Challenge.objects.filter(tenant=t, status='active').count()}\n"
    )


SYSTEM_PROMPT = (
    "تو «دستیار هوشمند موتوشاب» هستی؛ به فارسی، کوتاه و دقیق پاسخ بده. "
    "فقط بر پایهٔ «دادهٔ زندهٔ سامانه» که در اختیارت گذاشته می‌شود پاسخ بده و چیزی از خودت نساز. "
    "اگر داده پاسخ را پوشش نمی‌دهد، صادقانه بگو که در دادهٔ فعلی موجود نیست."
)


def _http_json(url, headers, payload, timeout=30):
    import json as _json
    import urllib.request
    req = urllib.request.Request(url, data=_json.dumps(payload).encode(), method="POST",
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _json.loads(resp.read())


def _openai_answer(question, context):
    """OpenAI-compatible chat API (Ollama, gateways, most providers)."""
    from django.conf import settings
    base = getattr(settings, "OPENAI_BASE_URL", "")
    if not base:
        return None
    headers = {}
    key = getattr(settings, "OPENAI_API_KEY", "")
    if key:
        headers["authorization"] = f"Bearer {key}"
    # OpenRouter (optional): identify the app for its rankings; ignored elsewhere.
    if getattr(settings, "OPENAI_HTTP_REFERER", ""):
        headers["HTTP-Referer"] = settings.OPENAI_HTTP_REFERER
    if getattr(settings, "OPENAI_APP_TITLE", ""):
        headers["X-Title"] = settings.OPENAI_APP_TITLE
    try:
        data = _http_json(
            base.rstrip("/") + "/chat/completions", headers,
            {"model": getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"), "max_tokens": 600,
             "messages": [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
                          {"role": "user", "content": question}]},
        )
        return (data["choices"][0]["message"]["content"] or "").strip() or None
    except Exception:
        return None


def _anthropic_answer(question, context):
    """Anthropic (Claude) Messages API."""
    from django.conf import settings
    key = getattr(settings, "ANTHROPIC_API_KEY", "")
    if not key:
        return None
    try:
        data = _http_json(
            getattr(settings, "ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages",
            {"x-api-key": key, "anthropic-version": "2023-06-01"},
            {"model": getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-5"), "max_tokens": 600,
             "system": SYSTEM_PROMPT + "\n\n" + context,
             "messages": [{"role": "user", "content": question}]},
        )
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        return text or None
    except Exception:
        return None


def _llm_answer(question, context):
    """Try a configured LLM (OpenAI-compatible first, then Anthropic), grounded in
    live data. Returns None when none configured / on any error → caller uses rules."""
    return _openai_answer(question, context) or _anthropic_answer(question, context)


class AssistantView(APIView):
    """Persian Q&A grounded in live tenant data. Uses an LLM (Claude) when
    ANTHROPIC_API_KEY is configured, otherwise a deterministic keyword matcher."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"suggestions": SUGGESTIONS})

    def post(self, request):
        t = request.tenant
        q = (request.data or {}).get("question", "")
        llm = _llm_answer(q, _live_context(t))
        if llm:
            return Response({"answer": llm, "source": "llm"})
        return Response({"answer": _rule_answer(t, q), "source": "rules"})


# ── Global cross-module search ───────────────────────────────────────────────
class SearchView(APIView):
    """Server-side search across modules → typed hits {id,type,title,snippet,to}."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q
        t = request.tenant
        q = (request.query_params.get("q") or "").strip()
        if not q or len(q) < 2:
            return Response({"results": []})
        hits = []
        cap = 8  # per module

        def add(qs, type_, title_f, snip_f, to_f):
            for o in qs[:cap]:
                hits.append({"id": str(o.id), "type": type_, "title": title_f(o),
                             "snippet": snip_f(o), "to": to_f(o)})

        # content
        from apps.content.models import BlogPost, Event, KnowledgeDoc, MediaItem, News
        add(News.objects.filter(tenant=t, title__icontains=q), "news",
            lambda o: o.title, lambda o: "خبر", lambda o: f"/dashboard/news/{o.id}")
        add(BlogPost.objects.filter(tenant=t, title__icontains=q), "blog",
            lambda o: o.title, lambda o: o.excerpt or "بلاگ", lambda o: f"/dashboard/blog/{o.id}")
        add(Event.objects.filter(tenant=t).filter(Q(title__icontains=q) | Q(location__icontains=q)), "event",
            lambda o: o.title, lambda o: o.location or "رویداد", lambda o: f"/dashboard/events/{o.id}")
        add(MediaItem.objects.filter(tenant=t, title__icontains=q), "media",
            lambda o: o.title, lambda o: o.album or "رسانه", lambda o: "/dashboard/media")
        add(KnowledgeDoc.objects.filter(tenant=t, title__icontains=q), "doc",
            lambda o: o.title, lambda o: o.category or "سند", lambda o: "/dashboard/knowledge")
        # social
        from apps.social.models import ForumTopic, Group
        add(Group.objects.filter(tenant=t, name__icontains=q), "group",
            lambda o: o.name, lambda o: o.category or "گروه", lambda o: f"/dashboard/groups/{o.id}")
        add(ForumTopic.objects.filter(tenant=t, title__icontains=q), "forum",
            lambda o: o.title, lambda o: o.category or "انجمن", lambda o: f"/dashboard/forum/{o.id}")
        from apps.accounts.models import User
        add(User.objects.filter(tenant=t).filter(Q(name__icontains=q) | Q(title__icontains=q)), "user",
            lambda o: o.name, lambda o: o.title or o.org or "کاربر", lambda o: f"/dashboard/profile/{o.id}")
        # process
        from apps.projects.models import Project
        add(Project.objects.filter(tenant=t).filter(Q(name__icontains=q) | Q(client__icontains=q)), "project",
            lambda o: o.name, lambda o: f"کارفرما: {o.client}" if o.client else "پروژه", lambda o: f"/dashboard/projects/{o.id}/board")
        add(Contract.objects.filter(tenant=t).filter(Q(title__icontains=q) | Q(vendor__icontains=q)), "contract",
            lambda o: o.title, lambda o: o.vendor or "قرارداد", lambda o: "/dashboard/contracts")
        add(NfProject.objects.filter(tenant=t).filter(Q(title_fa__icontains=q) | Q(code__icontains=q)), "nf",
            lambda o: f"{o.code} — {o.title_fa}", lambda o: o.team_name or "صندوق نوآور", lambda o: "/dashboard/funds")
        from apps.training.models import TrainingCourse
        add(TrainingCourse.objects.filter(tenant=t, title__icontains=q), "training",
            lambda o: o.title, lambda o: o.instructor or "دوره", lambda o: "/dashboard/training")
        from apps.chat.models import Channel
        add(Channel.objects.filter(tenant=t).filter(Q(name__icontains=q) | Q(topic__icontains=q)), "channel",
            lambda o: o.name, lambda o: o.topic or "کانال", lambda o: "/dashboard/chat")
        from apps.awards.models import AwardEntry
        add(AwardEntry.objects.filter(tenant=t).filter(Q(title__icontains=q) | Q(company__icontains=q)), "award",
            lambda o: o.title, lambda o: o.company or "جایزه", lambda o: "/dashboard/award")
        from apps.contracts.models import TechTransferContract
        add(TechTransferContract.objects.filter(tenant=t).filter(Q(title__icontains=q) | Q(company__icontains=q)), "transfer",
            lambda o: o.title, lambda o: o.company or "تبادل فناوری", lambda o: "/dashboard/contracts?tab=transfer")
        from apps.research.models import ResearchOpportunity
        add(ResearchOpportunity.objects.filter(tenant=t, title__icontains=q), "rfp",
            lambda o: o.title, lambda o: o.field or "فراخوان", lambda o: "/dashboard/research")
        return Response({"results": hits})
