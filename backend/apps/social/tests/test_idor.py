import json

from django.test import Client


def test_member_cannot_see_private_group(admin, member, tenant, auth):
    Client().post("/api/v1/groups", json.dumps({"name": "عمومی", "privacy": "public"}),
                  content_type="application/json", **auth(admin, tenant))
    priv = Client().post("/api/v1/groups", json.dumps({"name": "خصوصی", "privacy": "private"}),
                         content_type="application/json", **auth(admin, tenant)).json()["data"]
    lst = Client().get("/api/v1/groups", **auth(member, tenant)).json()
    assert lst["meta"]["count"] == 1  # only the public one
    assert Client().get(f"/api/v1/groups/{priv['id']}", **auth(member, tenant)).status_code == 404
