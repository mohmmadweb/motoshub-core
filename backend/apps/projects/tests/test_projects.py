import json
from django.test import Client


def _post(path, body, admin, tenant, auth):
    return Client().post(f"/api/v1/{path}", json.dumps(body), content_type="application/json", **auth(admin, tenant))


def test_project_and_task_crud(admin, tenant, auth):
    p = _post("projects", {"name": "پروژهٔ نمونه", "client": "بهنوش"}, admin, tenant, auth).json()["data"]
    assert p["name"] == "پروژهٔ نمونه"
    t = _post("tasks", {"project": p["id"], "title": "تسک اول", "status": "planning", "priority": "high"}, admin, tenant, auth)
    assert t.status_code == 201
    lst = Client().get(f"/api/v1/tasks?project={p['id']}", **auth(admin, tenant)).json()
    assert lst["meta"]["count"] == 1 and lst["data"][0]["status"] == "planning"


def test_projects_are_tenant_scoped(admin, tenant, auth):
    _post("projects", {"name": "پ"}, admin, tenant, auth)
    assert Client().get("/api/v1/projects", **auth(admin, tenant)).json()["meta"]["count"] == 1
