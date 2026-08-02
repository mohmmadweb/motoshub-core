"""Workflow jobs for the innovation fund (Celery). Wire to Celery beat in prod."""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .catalog import REVIEW_ESCALATION_DAYS


@shared_task
def escalate_overdue_report_reviews():
    """Flag report-chain steps still pending after the escalation window."""
    from .models import NfReportChainStep

    cutoff = timezone.now() - timedelta(days=REVIEW_ESCALATION_DAYS)
    qs = NfReportChainStep.objects.filter(status="pending", late=False, created_at__lt=cutoff)
    return qs.update(late=True)


@shared_task
def send_report_reminders():
    """Notify fund managers of reports due within the reminder window."""
    from datetime import timedelta
    from django.utils import timezone
    from apps.notifications.services import notify
    from .models import NfReport

    soon = timezone.now().date() + timedelta(days=7)
    count = 0
    for report in NfReport.objects.filter(status="pending_upload", due__lte=soon).select_related("project__fund_manager"):
        mgr = report.project.fund_manager
        if mgr:
            notify(mgr, f"گزارش «{report.title}» تا {report.due} باید بارگذاری شود.", kind="task", tenant=report.tenant)
            count += 1
    return count
