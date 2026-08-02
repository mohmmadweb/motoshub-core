import json

from django.test import Client

from apps.rbac.models import Role


def test_create_custom_role_and_protect_system(admin, tenant, auth):
    r = Client().post("/api/v1/roles", json.dumps({"title": "سفارشی", "scope": "tenant", "permissions": ["news.list"]}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 201 and r.json()["data"]["is_system"] is False

    sys_role = Role.objects.get(key="member")
    edit = Client().patch(f"/api/v1/roles/{sys_role.id}", json.dumps({"title": "x"}),
                          content_type="application/json", **auth(admin, tenant))
    assert edit.status_code == 403


def test_catalog_lists_permission_groups(admin, tenant, auth):
    r = Client().get("/api/v1/permissions/catalog", **auth(admin, tenant))
    assert r.status_code == 200 and len(r.json()["data"]) == 20


def test_user_create_and_list(admin, tenant, auth):
    c = Client().post("/api/v1/users", json.dumps({"username": "u2", "name": "کاربر", "password": "pass12345"}),
                      content_type="application/json", **auth(admin, tenant))
    assert c.status_code == 201
    lst = Client().get("/api/v1/users", **auth(admin, tenant)).json()
    assert lst["meta"]["count"] >= 2
