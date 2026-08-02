import json

from django.test import Client


def _post(user, tenant, auth, op, target):
    return Client().post(
        f"/api/v1/social/friends?do={op}",
        json.dumps({"user": str(target.id)}),
        content_type="application/json",
        **auth(user, tenant),
    )


def test_friend_request_accept_flow(admin, member, tenant, auth):
    # admin sends a request → outgoing for admin, incoming for member.
    assert _post(admin, tenant, auth, "request", member).status_code == 200
    admin_net = Client().get("/api/v1/social/friends", **auth(admin, tenant)).json()["data"]
    member_net = Client().get("/api/v1/social/friends", **auth(member, tenant)).json()["data"]
    assert admin_net["states"][str(member.id)] == "outgoing"
    assert member_net["states"][str(admin.id)] == "incoming"

    # member accepts → both see "friend".
    assert _post(member, tenant, auth, "accept", admin).status_code == 200
    assert Client().get("/api/v1/social/friends", **auth(admin, tenant)).json()["data"]["states"][str(member.id)] == "friend"

    # admin removes → relation gone for both.
    assert _post(admin, tenant, auth, "remove", member).status_code == 200
    assert str(member.id) not in Client().get("/api/v1/social/friends", **auth(admin, tenant)).json()["data"]["states"]


def test_follow_toggle(admin, member, tenant, auth):
    assert _post(admin, tenant, auth, "follow", member).status_code == 200
    assert str(member.id) in Client().get("/api/v1/social/friends", **auth(admin, tenant)).json()["data"]["following"]
    assert _post(admin, tenant, auth, "unfollow", member).status_code == 200
    assert str(member.id) not in Client().get("/api/v1/social/friends", **auth(admin, tenant)).json()["data"]["following"]


def test_cannot_befriend_self(admin, tenant, auth):
    assert _post(admin, tenant, auth, "request", admin).status_code == 422
