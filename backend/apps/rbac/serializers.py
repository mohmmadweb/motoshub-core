from rest_framework import serializers

from .models import Role, RoleAssignment


class RoleSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "key", "title", "description", "scope", "permissions", "is_system", "member_count", "created_at"]
        read_only_fields = ["id", "key", "is_system", "member_count", "created_at"]

    def get_member_count(self, obj):
        return obj.assignments.count()


class RoleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleAssignment
        fields = ["id", "user", "role", "tenant", "holding", "company"]
        read_only_fields = ["id", "tenant"]
