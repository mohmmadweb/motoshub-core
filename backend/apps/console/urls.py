from django.urls import path
from rest_framework.routers import DefaultRouter

from .backups import BackupDownloadView, BackupView
from .storage import StorageUsageView, ThumbnailRebuildView
from .views import (
    AssistantView,
    ReportDimensionsView,
    ReportExportView,
    ReportSummaryView,
    ReportTimeseriesView,
    GuestAccountViewSet,
    IntegrationViewSet,
    SavedReportViewSet,
    SearchView,
    WorkflowSettingsView,
)

router = DefaultRouter(trailing_slash=False)
router.register("reports/saved", SavedReportViewSet, basename="saved-report")
router.register("integrations", IntegrationViewSet, basename="integration")
router.register("guest-accounts", GuestAccountViewSet, basename="guest-account")

urlpatterns = router.urls + [
    path("settings/workflow", WorkflowSettingsView.as_view(), name="workflow-settings"),
    path("reports/summary", ReportSummaryView.as_view(), name="report-summary"),
    path("reports/dimensions", ReportDimensionsView.as_view(), name="report-dimensions"),
    path("reports/export", ReportExportView.as_view(), name="report-export"),
    path("reports/timeseries", ReportTimeseriesView.as_view(), name="report-timeseries"),
    path("assistant/suggestions", AssistantView.as_view(), name="assistant-suggestions"),
    path("assistant/ask", AssistantView.as_view(), name="assistant-ask"),
    path("search", SearchView.as_view(), name="search"),
    path("settings/storage", StorageUsageView.as_view(), name="storage-usage"),
    path("settings/storage/thumbnails", ThumbnailRebuildView.as_view(), name="thumbnail-rebuild"),
    path("settings/backups", BackupView.as_view(), name="backups"),
    path("settings/backups/<str:name>", BackupDownloadView.as_view(), name="backup-file"),
]
