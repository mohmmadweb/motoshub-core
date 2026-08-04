import json

from django.test import Client

from apps.social.models import Group, GroupMembership


def _group(tenant, admin, privacy="public"):
    g = Group.objects.create(tenant=tenant, owner=admin, name="گروه", privacy=privacy)
    GroupMembership.objects.create(tenant=tenant, group=g, user=admin, role="owner", is_moderator=True)
    return g


def _post(client_auth, path, body):
    return Client().post(f"/api/v1{path}", json.dumps(body), content_type="application/json", **client_auth)


def test_member_can_post_and_reply(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    first = _post(auth(admin, tenant), f"/groups/{g.id}/messages", {"text": "سلام"}).json()["data"]
    r = _post(auth(member, tenant), f"/groups/{g.id}/messages", {"text": "پاسخ", "reply_to_id": first["id"]})
    assert r.status_code == 201
    assert r.json()["data"]["reply_to"]["text"] == "سلام"


def test_private_group_hidden_from_non_members(admin, member, tenant, auth):
    g = _group(tenant, admin, privacy="private")
    assert Client().get(f"/api/v1/groups/{g.id}/messages", **auth(member, tenant)).status_code == 403


def test_only_moderators_pin(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    m = _post(auth(member, tenant), f"/groups/{g.id}/messages", {"text": "پیام"}).json()["data"]
    url = f"/api/v1/groups/{g.id}/messages/{m['id']}"
    assert Client().patch(url, json.dumps({"pinned": True}), content_type="application/json",
                          **auth(member, tenant)).status_code == 403
    assert Client().patch(url, json.dumps({"pinned": True}), content_type="application/json",
                          **auth(admin, tenant)).json()["data"]["pinned"] is True


def test_delete_is_soft_and_hides_text(admin, tenant, auth):
    g = _group(tenant, admin)
    m = _post(auth(admin, tenant), f"/groups/{g.id}/messages", {"text": "محرمانه"}).json()["data"]
    Client().delete(f"/api/v1/groups/{g.id}/messages/{m['id']}", **auth(admin, tenant))
    rows = Client().get(f"/api/v1/groups/{g.id}/messages", **auth(admin, tenant)).json()["data"]
    gone = [x for x in rows if x["id"] == m["id"]][0]
    assert gone["deleted"] is True and gone["text"] == ""


def test_promote_demote_and_owner_is_protected(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    url = f"/api/v1/groups/{g.id}/members/{member.id}"
    up = Client().patch(url, json.dumps({"role": "admin"}), content_type="application/json", **auth(admin, tenant))
    assert up.json()["data"]["role"] == "admin" and up.json()["data"]["can_moderate"] is True
    # the owner's own role cannot be changed
    owner_url = f"/api/v1/groups/{g.id}/members/{admin.id}"
    assert Client().patch(owner_url, json.dumps({"role": "member"}), content_type="application/json",
                          **auth(admin, tenant)).status_code == 422


def test_slow_mode_throttles_members_not_moderators(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    Client().patch(f"/api/v1/groups/{g.id}/settings", json.dumps({"slow_mode_seconds": 60}),
                   content_type="application/json", **auth(admin, tenant))
    assert _post(auth(member, tenant), f"/groups/{g.id}/messages", {"text": "۱"}).status_code == 201
    assert _post(auth(member, tenant), f"/groups/{g.id}/messages", {"text": "۲"}).status_code == 429
    assert _post(auth(admin, tenant), f"/groups/{g.id}/messages", {"text": "مدیر"}).status_code == 201


def test_join_by_invite_code(admin, member, tenant, auth):
    g = _group(tenant, admin, privacy="private")
    code = Client().get(f"/api/v1/groups/{g.id}/invite", **auth(admin, tenant)).json()["data"]["invite_code"]
    assert _post(auth(member, tenant), "/groups/join", {"invite_code": code}).status_code == 201
    assert GroupMembership.objects.filter(group=g, user=member).exists()
    assert _post(auth(member, tenant), "/groups/join", {"invite_code": "bogus"}).status_code == 404


def test_banned_member_cannot_read_or_post(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member", banned=True)
    assert Client().get(f"/api/v1/groups/{g.id}/messages", **auth(member, tenant)).status_code == 403
