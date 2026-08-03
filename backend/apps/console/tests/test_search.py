import json
from django.test import Client

from apps.projects.models import Project


def test_search_finds_across_modules(admin, tenant, auth):
    Project.objects.create(tenant=tenant, name="سامانهٔ پایش انرژی", client="بهنوش")
    Client().post("/api/v1/news", json.dumps({"title": "افتتاح سامانهٔ نو", "summary": "..."}),
                  content_type="application/json", **auth(admin, tenant))
    d = Client().get("/api/v1/search?q=سامانه", **auth(admin, tenant)).json()["data"]["results"]
    types = {h["type"] for h in d}
    assert "project" in types and "news" in types
    assert all({"id", "type", "title", "to"} <= set(h) for h in d)


def test_search_ignores_short_query(admin, tenant, auth):
    assert Client().get("/api/v1/search?q=ا", **auth(admin, tenant)).json()["data"]["results"] == []
