from django.urls import path

from .views import ReportSummaryView, WorkflowSettingsView

urlpatterns = [
    path("settings/workflow", WorkflowSettingsView.as_view(), name="workflow-settings"),
    path("reports/summary", ReportSummaryView.as_view(), name="report-summary"),
]
