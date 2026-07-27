from rest_framework import serializers

from apps.content.serializers import AuthorField

from .models import Contract, ContractApproval, ContractPayment


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
