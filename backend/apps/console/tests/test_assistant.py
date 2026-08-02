import json

from django.test import Client

from apps.projects.models import Project


def test_assistant_answers_from_live_data(admin, tenant, auth):
    Project.objects.create(tenant=tenant, name="پ۱", health="green")
    Project.objects.create(tenant=tenant, name="پ۲", health="red")
    r = Client().post("/api/v1/assistant/ask", json.dumps({"question": "سلامت پورتفولیو چگونه است؟"}),
                      content_type="application/json", **auth(admin, tenant))
    ans = r.json()["data"]["answer"]
    assert "سبز" in ans and "قرمز" in ans  # reflects the two live projects


def test_assistant_suggestions(admin, tenant, auth):
    d = Client().get("/api/v1/assistant/suggestions", **auth(admin, tenant)).json()["data"]
    assert isinstance(d["suggestions"], list) and len(d["suggestions"]) >= 3
