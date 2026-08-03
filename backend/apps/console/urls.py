from django.urls import path

from .views import AssistantView, ReportSummaryView, SearchView, WorkflowSettingsView

urlpatterns = [
    path("settings/workflow", WorkflowSettingsView.as_view(), name="workflow-settings"),
    path("reports/summary", ReportSummaryView.as_view(), name="report-summary"),
    path("assistant/suggestions", AssistantView.as_view(), name="assistant-suggestions"),
    path("assistant/ask", AssistantView.as_view(), name="assistant-ask"),
    path("search", SearchView.as_view(), name="search"),
]
