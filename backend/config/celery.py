import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("motoshub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from celery.schedules import crontab  # noqa: E402

# Scheduled workflow jobs (mirrors the prototype's workflow rules).
app.conf.beat_schedule = {
    "escalate-overdue-report-reviews": {
        "task": "apps.fund.tasks.escalate_overdue_report_reviews",
        "schedule": crontab(hour=6, minute=0),  # daily 06:00
    },
    "fund-report-reminders": {
        "task": "apps.fund.tasks.send_report_reminders",
        "schedule": crontab(hour=7, minute=0),  # daily 07:00
    },
}
