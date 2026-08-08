from rest_framework import serializers

from .models import Company, Holding, Tenant


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "holding"]


class HoldingSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)

    class Meta:
        model = Holding
        fields = ["id", "name", "color", "companies", "created_at"]
        read_only_fields = ["id", "companies", "created_at"]


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "short_name", "domain", "logo_color", "plan",
                  "enabled_modules", "cross_tenant",
                  "sso_provider", "sso_url", "sso_auto_create", "sso_allow_local",
                  "created_at"]
        read_only_fields = ["id", "domain", "created_at"]
