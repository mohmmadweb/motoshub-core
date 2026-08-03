import json
from django.test import Client


def test_poll_create_and_vote(admin, tenant, auth):
    p = Client().post("/api/v1/polls", json.dumps({"question": "کدام؟", "option_labels": ["الف", "ب"]}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert len(p["options"]) == 2
    opt = p["options"][0]["id"]
    r = Client().post(f"/api/v1/polls/{p['id']}/vote", json.dumps({"option_id": opt}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert r["voted"] == opt and r["results"][opt] == 1


def test_poll_rejects_bad_option(admin, tenant, auth):
    p = Client().post("/api/v1/polls", json.dumps({"question": "س", "option_labels": ["x"]}),
                      content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert Client().post(f"/api/v1/polls/{p['id']}/vote", json.dumps({"option_id": "bad"}),
                         content_type="application/json", **auth(admin, tenant)).status_code == 422
