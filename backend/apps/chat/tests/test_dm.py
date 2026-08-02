import json

from django.test import Client


def test_send_and_list_dm(admin, member, tenant, auth):
    r = Client().post("/api/v1/chat/dms", json.dumps({"to": str(member.id), "text": "سلام"}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 201 and r.json()["data"]["from"] == "me"
    # admin sees one thread with member; member sees it as unread incoming.
    a = Client().get("/api/v1/chat/dms", **auth(admin, tenant)).json()["data"]
    assert len(a) == 1 and a[0]["with"] == member.name and a[0]["messages"][0]["from"] == "me"
    m = Client().get("/api/v1/chat/dms", **auth(member, tenant)).json()["data"]
    assert m[0]["unread"] == 1 and m[0]["messages"][0]["from"] == "them"


def test_dm_requires_valid_target(admin, tenant, auth):
    r = Client().post("/api/v1/chat/dms", json.dumps({"to": str(admin.id), "text": "به خودم"}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 422  # cannot DM yourself
