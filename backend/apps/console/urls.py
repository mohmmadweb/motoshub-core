from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AssistantView,
    ReportDimensionsView,
    ReportSummaryView,
    ReportTimeseriesView,
    SavedReportViewSet,
    SearchView,
    WorkflowSettingsView,
)

router = DefaultRouter(trailing_slash=False)
router.register("reports/saved", SavedReportViewSet, basename="saved-report")

urlpatterns = router.urls + [
    path("settings/workflow", WorkflowSettingsView.as_view(), name="workflow-settings"),
    path("reports/summary", ReportSummaryView.as_view(), name="report-summary"),
    path("reports/dimensions", ReportDimensionsView.as_view(), name="report-dimensions"),
    path("reports/timeseries", ReportTimeseriesView.as_view(), name="report-timeseries"),
    path("assistant/suggestions", AssistantView.as_view(), name="assistant-suggestions"),
    path("assistant/ask", AssistantView.as_view(), name="assistant-ask"),
    path("search", SearchView.as_view(), name="search"),
]
