from rest_framework import serializers

from .models import NfGuarantee, NfPayment, NfProject, NfReport, NfReportChainStep, NfRequest


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

    class Meta:
        model = NfProject
        fields = ["id", "code", "title_fa", "title_en", "field", "macro_field",
                  "rahbar", "nazer", "fund_manager", "budget", "share_percent",
                  "duration_months", "contract_no", "stage", "sub_status", "green_path",
                  "progress", "screening_score", "jury_score", "team_name", "team_type",
                  "team_city", "guarantees", "reports", "payments", "requests",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "fund_manager", "guarantees", "reports", "payments",
                            "requests", "created_at", "updated_at"]
