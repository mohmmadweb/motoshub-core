from rest_framework import serializers

from .models import ResearchApplication, ResearchOpportunity, RfpCall, RfpVendor, Sabbatical, SabbaticalReport


class ResearchApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchApplication
        fields = ["id", "opportunity", "applicant_name", "affiliation", "score", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class ResearchOpportunitySerializer(serializers.ModelSerializer):
    applicant_count = serializers.IntegerField(read_only=True)
    applications = ResearchApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchOpportunity
        fields = ["id", "title", "field", "stage", "budget", "supervisor", "deadline",
                  "applicant_count", "applications", "created_at", "updated_at"]
        read_only_fields = ["id", "applicant_count", "applications", "created_at", "updated_at"]


# ── RFP + Sabbatical ────────────────────────────────────────────────────────
class RfpVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfpVendor
        fields = ["id", "name", "biz_score", "tech_score", "price_opened", "price", "winner"]


class RfpCallSerializer(serializers.ModelSerializer):
    vendors = RfpVendorSerializer(many=True, read_only=True)

    class Meta:
        model = RfpCall
        fields = ["id", "title", "company", "holding", "stage", "deadline", "channels", "vendors", "created_at"]
        read_only_fields = ["id", "vendors", "created_at"]


class SabbaticalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SabbaticalReport
        fields = ["id", "no", "title", "status", "paid_amount"]


class SabbaticalSerializer(serializers.ModelSerializer):
    reports = SabbaticalReportSerializer(many=True, read_only=True)

    class Meta:
        model = Sabbatical
        fields = ["id", "professor", "university", "industry", "topic", "trl_before",
                  "trl_after", "contract", "stage", "reports", "created_at"]
        read_only_fields = ["id", "reports", "created_at"]
