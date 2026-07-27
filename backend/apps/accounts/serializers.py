from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    tenant_id = serializers.UUIDField(read_only=True)
    company_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "name", "title", "email", "avatar_color",
            "skills", "presence", "tenant_id", "company_id", "permissions",
        ]
        read_only_fields = fields

    def get_permissions(self, obj):
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request else None
        return sorted(obj.get_permission_ids(tenant))


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
