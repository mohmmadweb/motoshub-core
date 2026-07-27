from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.awards.models import AwardEntry
from apps.contracts.models import Contract
from apps.fund.models import NfProject
from apps.projects.models import Project
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
                "funds": NfProject.objects.filter(tenant=t).count(),
                "tickets": Ticket.objects.filter(tenant=t).count(),
                "award_entries": AwardEntry.objects.filter(tenant=t).count(),
            },
            "projects_by_health": by(Project.objects, "health"),
            "contracts_by_stage": by(Contract.objects, "stage"),
            "funds_by_stage": by(NfProject.objects, "stage"),
            "tickets_by_status": by(Ticket.objects, "status"),
        })
