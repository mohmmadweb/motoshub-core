import json

from django.test import Client


def _create(admin, tenant, auth, **over):
    payload = {"code": "NF-1405-0009", "title_fa": "طرح", "stage": "screening", **over}
    return Client().post("/api/v1/funds/projects", json.dumps(payload),
                         content_type="application/json", **auth(admin, tenant)).json()["data"]


def test_advance_blocked_below_screening_threshold(admin, tenant, auth):
    p = _create(admin, tenant, auth)
    r = Client().post(f"/api/v1/funds/projects/{p['id']}/advance", **auth(admin, tenant))
    assert r.status_code == 422


def test_advance_allowed_after_passing(admin, tenant, auth):
    p = _create(admin, tenant, auth)
    Client().post(f"/api/v1/funds/projects/{p['id']}/score",
                  json.dumps({"screening_score": 150}), content_type="application/json", **auth(admin, tenant))
    r = Client().post(f"/api/v1/funds/projects/{p['id']}/advance", **auth(admin, tenant))
    assert r.status_code == 200 and r.json()["data"]["stage"] == "jury"
