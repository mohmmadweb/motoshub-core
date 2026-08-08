"""Delegation: nobody may hand out authority they do not hold themselves."""
import json

import pytest
from django.test import Client

from apps.rbac.models import Role, RoleAssignment


def _post(path, payload, headers):
    return Client().post(path, json.dumps(payload), content_type="application/json", **headers)


@pytest.mark.django_db
def test_a_role_cannot_grant_more_than_its_author_holds(admin, tenant, auth):
    """An org admin lacks settings.system, so a role carrying it is refused.

    Otherwise anyone with roles.create could mint an all-powerful role and
    assign it to themselves — escalation in two clicks.
    """
    res = _post("/api/v1/roles", {
        "title": "نقش پرقدرت",
        "scope": "tenant",
        "permissions": ["news.list", "settings.system"],
    }, auth(admin, tenant))
    assert res.status_code == 403
    assert "settings.system" in res.json()["error"]["message"]
    assert not Role.objects.filter(title="نقش پرقدرت").exists()


@pytest.mark.django_db
def test_a_role_within_the_authors_own_rights_is_allowed(admin, tenant, auth):
    res = _post("/api/v1/roles", {
        "title": "ناظر اخبار",
        "scope": "tenant",
        "permissions": ["news.list", "news.create"],
    }, auth(admin, tenant))
    assert res.status_code == 201
    assert Role.objects.filter(title="ناظر اخبار").exists()


@pytest.mark.django_db
def test_a_platform_admin_may_grant_everything_they_hold(platform_admin, tenant, auth):
    res = _post("/api/v1/roles", {
        "title": "نقش کامل",
        "scope": "tenant",
        "permissions": ["settings.system", "settings.storage"],
    }, auth(platform_admin, tenant))
    assert res.status_code == 201


@pytest.mark.django_db
def test_editing_a_role_cannot_smuggle_in_extra_rights(admin, tenant, auth):
    role = Role.objects.create(tenant=tenant, title="نقش ساده", scope="tenant",
                               permissions=["news.list"], is_system=False)
    res = Client().put(
        f"/api/v1/roles/{role.id}",
        json.dumps({"title": "نقش ساده", "scope": "tenant",
                    "permissions": ["news.list", "settings.system"]}),
        content_type="application/json", **auth(admin, tenant),
    )
    assert res.status_code == 403
    role.refresh_from_db()
    assert "settings.system" not in role.permissions


@pytest.mark.django_db
def test_assigning_an_overpowered_role_is_refused(admin, member, tenant, auth):
    """The same escalation from the other side: handing someone a role that
    already outranks you."""
    strong = Role.objects.get(key="platform-admin")
    res = _post("/api/v1/role-assignments", {
        "user": str(member.id), "role": str(strong.id),
    }, auth(admin, tenant))
    assert res.status_code == 403
    assert not RoleAssignment.objects.filter(user=member, role=strong).exists()


@pytest.mark.django_db
def test_assigning_a_role_within_your_rights_works(admin, member, tenant, auth):
    ordinary = Role.objects.get(key="member")
    RoleAssignment.objects.filter(user=member).delete()
    res = _post("/api/v1/role-assignments", {
        "user": str(member.id), "role": str(ordinary.id),
    }, auth(admin, tenant))
    assert res.status_code == 201


@pytest.mark.django_db
def test_preset_roles_stay_read_only(admin, tenant, auth):
    preset = Role.objects.get(key="member")
    res = Client().put(
        f"/api/v1/roles/{preset.id}",
        json.dumps({"title": "دستکاری‌شده", "scope": "group", "permissions": ["news.list"]}),
        content_type="application/json", **auth(admin, tenant),
    )
    assert res.status_code == 403
    preset.refresh_from_db()
    assert preset.title != "دستکاری‌شده"
