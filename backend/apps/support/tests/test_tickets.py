import json
from django.test import Client


def test_ticket_create_gets_number(admin, tenant, auth):
    t = Client().post("/api/v1/tickets", json.dumps({"subject": "مشکل", "category": "فنی", "priority": "urgent"}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert t["subject"] == "مشکل" and t["number"]  # auto-assigned ticket number
    assert Client().get("/api/v1/tickets", **auth(admin, tenant)).json()["meta"]["count"] == 1
