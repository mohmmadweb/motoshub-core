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
