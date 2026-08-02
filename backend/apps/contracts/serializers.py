from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import (
    Contract,
    ContractApproval,
    ContractPayment,
    ESignDocument,
    ESignStep,
    Tender,
    TechTransferContract,
)


class ContractPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractPayment
        fields = ["id", "contract", "title", "amount", "due", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContractApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractApproval
        fields = ["id", "contract", "role", "name", "status", "order", "acted_at", "created_at"]
        read_only_fields = ["id", "acted_at", "created_at"]


class ContractSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)
    payments = ContractPaymentSerializer(many=True, read_only=True)
    approvals = ContractApprovalSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = ["id", "title", "vendor", "stage", "contract_type", "method", "value",
                  "guarantee", "deadline", "owner", "payments", "approvals", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "payments", "approvals", "created_at", "updated_at"]


class ContractListSerializer(serializers.ModelSerializer):
    owner = AuthorField(read_only=True)

    class Meta:
        model = Contract
        fields = ["id", "title", "vendor", "stage", "contract_type", "value", "deadline", "owner", "created_at"]
        read_only_fields = fields


# ── Rich Daneshmand sub-modules ──────────────────────────────────────────────
class TechTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechTransferContract
        fields = ["id", "kind", "title", "nazer", "city", "holding", "company", "mojri",
                  "company_role", "daneshmand_role", "amount", "commitment",
                  "physical_progress", "time_progress", "financial_progress",
                  "guarantee", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ["id", "title", "method", "stage", "participants",
                  "session_date", "winner", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class ESignStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESignStep
        fields = ["id", "role", "name", "status", "date", "order"]


class ESignDocumentSerializer(serializers.ModelSerializer):
    steps = ESignStepSerializer(many=True, read_only=True)

    class Meta:
        model = ESignDocument
        fields = ["id", "title", "kind", "related_to", "method", "letter_no", "steps", "created_at"]
        read_only_fields = ["id", "steps", "created_at"]
