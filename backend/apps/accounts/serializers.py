from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    tenant_id = serializers.UUIDField(read_only=True)
    company_id = serializers.UUIDField(read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True, default="")

    class Meta:
        model = User
        fields = [
            "id", "username", "name", "title", "org", "email", "avatar_color",
            "skills", "presence", "tenant_id", "company_id", "company_name", "permissions",
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


class UserAdminSerializer(serializers.ModelSerializer):
    role_ids = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # The company a person belongs to is their access domain, so the console
    # shows it beside the role rather than leaving it implicit.
    company_name = serializers.CharField(source="company.name", read_only=True, default="")

    class Meta:
        model = User
        fields = ["id", "username", "name", "title", "org", "email", "avatar_color",
                  "skills", "is_active", "presence", "role_ids", "company_name",
                  "password", "date_joined"]
        read_only_fields = ["id", "role_ids", "date_joined"]

    def get_role_ids(self, obj):
        return [str(a.role_id) for a in obj.role_assignments.all()]

    def create(self, validated_data):
        pwd = validated_data.pop("password", None) or "changeme123"
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance
