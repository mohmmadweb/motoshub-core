from rest_framework import serializers

from .models import Fund, NfGuarantee, NfPayment, NfProject, NfReport, NfReportChainStep, NfRequest, FundTranche, FundKpi, ReviewSession, FundEntity, SeedInvestment


class NfGuaranteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NfGuarantee
        fields = ["id", "kind", "amount", "status"]


class NfChainStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = NfReportChainStep
        fields = ["id", "role", "name", "status", "late", "order"]


class NfReportSerializer(serializers.ModelSerializer):
    chain = NfChainStepSerializer(many=True, read_only=True)

    class Meta:
        model = NfReport
        fields = ["id", "report_type", "title", "due", "uploaded_at", "status", "chain"]


class NfPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NfPayment
        fields = ["id", "payment_type", "title", "amount", "status", "doc_no"]


class NfRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NfRequest
        fields = ["id", "request_type", "note", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class NfProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NfProject
        fields = ["id", "code", "title_fa", "field", "rahbar", "budget", "stage",
                  "sub_status", "green_path", "progress", "created_at"]
        read_only_fields = fields


class NfProjectSerializer(serializers.ModelSerializer):
    guarantees = NfGuaranteeSerializer(many=True, read_only=True)
    reports = NfReportSerializer(many=True, read_only=True)
    payments = NfPaymentSerializer(many=True, read_only=True)
    requests = NfRequestSerializer(many=True, read_only=True)
    fund_manager_name = serializers.CharField(source="fund_manager.name", read_only=True, default="")

    class Meta:
        model = NfProject
        fields = ["id", "code", "title_fa", "title_en", "field", "macro_field",
                  "mother_project", "rahbar", "nazer", "fund_manager", "budget",
                  "share_percent", "duration_months", "contract_no", "stage",
                  "sub_status", "green_path", "progress", "screening_score", "jury_score", "screening_scores", "jury_dimensions",
                  "team_name", "team_type", "team_city", "team_manager", "team_members",
                  "fund_manager_name", "finance", "gantt", "timeline",
                  "guarantees", "reports", "payments", "requests",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "fund_manager", "guarantees", "reports", "payments",
                            "requests", "created_at", "updated_at"]


class FundTrancheSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTranche
        fields = ["id", "title", "amount", "condition", "status"]


class FundKpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundKpi
        fields = ["id", "label", "value", "target", "on_track"]


class ReviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSession
        fields = ["id", "title", "date", "items", "committee", "created_at"]
        read_only_fields = ["id", "created_at"]


class FundSerializer(serializers.ModelSerializer):
    tranches = FundTrancheSerializer(many=True, read_only=True)
    kpis = FundKpiSerializer(many=True, read_only=True)

    class Meta:
        model = Fund
        fields = ["id", "title", "applicant", "stage", "amount", "roi", "requested", "approved",
                  "score", "committee", "region", "field", "notes", "tranches", "kpis", "created_at"]
        read_only_fields = ["id", "tranches", "kpis", "created_at"]


class FundEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundEntity
        fields = ["id", "name", "focus", "trl_range", "manager", "active_projects", "capital", "created_at"]
        read_only_fields = ["id", "created_at"]


class SeedInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeedInvestment
        fields = ["id", "startup", "field", "stage", "requested", "approved", "equity_percent",
                  "valuation", "kpi_status", "exit_plan", "created_at"]
        read_only_fields = ["id", "created_at"]
