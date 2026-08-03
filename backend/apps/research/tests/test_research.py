import json
from django.test import Client


def test_research_opportunity_crud(admin, tenant, auth):
    r = Client().post("/api/v1/research", json.dumps({"title": "فراخوان پژوهشی", "field": "هوش مصنوعی", "stage": "open"}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert r["stage"] == "open"
    assert Client().get("/api/v1/research", **auth(admin, tenant)).json()["meta"]["count"] == 1
