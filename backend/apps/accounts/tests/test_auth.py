"""Seed of the L1 test suite: auth + envelope + RBAC gating + tenant isolation."""
import pytest
from django.test import Client

from apps.accounts.models import User
from apps.accounts.tokens import issue_access
from apps.content.models import News
from apps.rbac.catalog import preset_roles
from apps.rbac.models import Role, RoleAssignment
from apps.tenancy.models import Tenant


@pytest.fixture
def seeded(db):
    for spec in preset_roles():
        Role.objects.update_or_create(key=spec["key"], tenant=None, defaults={
            "title": spec["title"], "scope": spec["scope"], "permissions": spec["permissions"], "is_system": True})
    t = Tenant.objects.create(name="بنیاد", domain="b.shub.ir")
    admin = User.objects.create_user("admin", password="x", name="مدیر", tenant=t)
    member = User.objects.create_user("member", password="x", name="عضو", tenant=t)
    RoleAssignment.objects.create(user=admin, role=Role.objects.get(key="org-admin"), tenant=t)
    RoleAssignment.objects.create(user=member, role=Role.objects.get(key="member"), tenant=t)
    return t, admin, member


def auth(u, t):
    return {"HTTP_AUTHORIZATION": f"Bearer {issue_access(u, t.id)}"}


def test_login_returns_token_and_permissions(seeded):
    Client()
    r = Client().post("/api/v1/auth/login", {"username": "admin", "password": "x"}, content_type="application/json")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "access" in data and "refresh" in data
    assert len(data["user"]["permissions"]) > 50


def test_me_requires_auth(seeded):
    r = Client().get("/api/v1/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["type"] == "unauthenticated"


def test_envelope_shape_on_list(seeded):
    t, admin, _ = seeded
    r = Client().get("/api/v1/news", **auth(admin, t))
    assert set(r.json().keys()) == {"data", "links", "meta"}


def test_rbac_blocks_member_create(seeded):
    t, _, member = seeded
    r = Client().post("/api/v1/news", {"title": "x"}, content_type="application/json", **auth(member, t))
    assert r.status_code == 403
    assert r.json()["error"]["type"] == "forbidden"


def test_tenant_isolation(seeded):
    t, admin, _ = seeded
    News.objects.create(tenant=t, title="خبر", author=admin)
    other = Tenant.objects.create(name="دیگر", domain="o.shub.ir")
    other_admin = User.objects.create_user("oa", password="x", name="م۲", tenant=other)
    RoleAssignment.objects.create(user=other_admin, role=Role.objects.get(key="org-admin"), tenant=other)
    r = Client().get("/api/v1/news", **auth(other_admin, other))
    assert r.json()["meta"]["count"] == 0
