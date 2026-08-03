import json
from django.test import Client


def test_track_with_entries(admin, tenant, auth):
    tr = Client().post("/api/v1/awards/tracks", json.dumps({"title": "محور", "categories": ["الف", "ب"]}),
                       content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert tr["categories"] == ["الف", "ب"]
    Client().post("/api/v1/awards/entries", json.dumps({"track": tr["id"], "title": "اثر", "company": "ج"}),
                  content_type="application/json", **auth(admin, tenant))
    got = Client().get("/api/v1/awards/tracks", **auth(admin, tenant)).json()["data"][0]
    assert got["submission_count"] == 1 and got["entries"][0]["title"] == "اثر"
