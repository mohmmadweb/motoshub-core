import pytest

from apps.accounts.models import User
from apps.rbac.catalog import preset_roles
from apps.rbac.models import Role, RoleAssignment
from apps.tenancy.models import Tenant


def _seed_roles():
    for spec in preset_roles():
        Role.objects.update_or_create(key=spec["key"], tenant=None, defaults={
            "title": spec["title"], "scope": spec["scope"],
            "permissions": spec["permissions"], "is_system": True})


@pytest.fixture
def tenant(db):
    _seed_roles()
    return Tenant.objects.create(name="بنیاد", domain="b.shub.ir")


@pytest.fixture
def admin(tenant):
    u = User.objects.create_user("admin", password="x", name="مدیر", tenant=tenant)
    RoleAssignment.objects.create(user=u, role=Role.objects.get(key="org-admin"), tenant=tenant)
    return u


@pytest.fixture
def member(tenant):
    u = User.objects.create_user("member", password="x", name="عضو", tenant=tenant)
    RoleAssignment.objects.create(user=u, role=Role.objects.get(key="member"), tenant=tenant)
    return u


@pytest.fixture
def auth():
    from apps.accounts.tokens import issue_access

    def _h(user, t):
        return {"HTTP_AUTHORIZATION": f"Bearer {issue_access(user, t.id)}"}
    return _h
