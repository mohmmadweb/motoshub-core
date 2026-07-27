"""Idempotently create/refresh the preset (system) roles from the code catalog."""
from django.core.management.base import BaseCommand

from apps.rbac.catalog import preset_roles
from apps.rbac.models import Role


class Command(BaseCommand):
    help = "Seed preset RBAC roles from apps.rbac.catalog"

    def handle(self, *args, **options):
        created = 0
        for spec in preset_roles():
            role, was_created = Role.objects.update_or_create(
                key=spec["key"],
                tenant=None,
                defaults={
                    "title": spec["title"],
                    "scope": spec["scope"],
                    "permissions": spec["permissions"],
                    "is_system": True,
                },
            )
            created += int(was_created)
            self.stdout.write(f"  {'+' if was_created else '='} {role.title} ({len(role.permissions)} perms)")
        self.stdout.write(self.style.SUCCESS(f"RBAC seeded ({created} new)."))
