import json

from django.core import mail
from django.test import Client

from apps.social.models import Group, GroupMembership, GroupTopic


def _group(tenant, admin):
    g = Group.objects.create(tenant=tenant, owner=admin, name="گروه", privacy="public")
    GroupMembership.objects.create(tenant=tenant, group=g, user=admin, role="owner", is_moderator=True)
    return g


def _post(headers, path, body):
    return Client().post(f"/api/v1{path}", json.dumps(body), content_type="application/json", **headers)


def test_first_topic_switches_group_to_forum_mode(admin, tenant, auth):
    g = _group(tenant, admin)
    assert g.topics_enabled is False
    r = _post(auth(admin, tenant), f"/groups/{g.id}/topics", {"name": "اعلان‌ها", "icon": "📢"})
    assert r.status_code == 201
    g.refresh_from_db()
    assert g.topics_enabled is True


def test_messages_are_scoped_to_their_topic(admin, tenant, auth):
    g = _group(tenant, admin)
    t = _post(auth(admin, tenant), f"/groups/{g.id}/topics", {"name": "پرسش"}).json()["data"]
    _post(auth(admin, tenant), f"/groups/{g.id}/messages", {"text": "در تاپیک", "topic_id": t["id"]})
    _post(auth(admin, tenant), f"/groups/{g.id}/messages", {"text": "در فید", "topic_id": "main"})

    in_topic = Client().get(f"/api/v1/groups/{g.id}/messages?topic={t['id']}", **auth(admin, tenant)).json()["data"]
    in_main = Client().get(f"/api/v1/groups/{g.id}/messages?topic=main", **auth(admin, tenant)).json()["data"]
    assert [m["text"] for m in in_topic] == ["در تاپیک"]
    assert [m["text"] for m in in_main] == ["در فید"]


def test_closed_topic_accepts_moderators_only(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    t = _post(auth(admin, tenant), f"/groups/{g.id}/topics", {"name": "بسته"}).json()["data"]
    Client().patch(f"/api/v1/groups/{g.id}/topics/{t['id']}", json.dumps({"closed": True}),
                   content_type="application/json", **auth(admin, tenant))
    assert _post(auth(member, tenant), f"/groups/{g.id}/messages",
                 {"text": "x", "topic_id": t["id"]}).status_code == 403
    assert _post(auth(admin, tenant), f"/groups/{g.id}/messages",
                 {"text": "ok", "topic_id": t["id"]}).status_code == 201


def test_mention_emails_the_mentioned_member(admin, member, tenant, auth):
    member.email = "member@example.ir"
    member.save(update_fields=["email"])
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    mail.outbox.clear()
    _post(auth(admin, tenant), f"/groups/{g.id}/messages",
          {"text": "@عضو لطفاً ببین", "mentions": [str(member.id)]})
    assert len(mail.outbox) == 1
    assert "member@example.ir" in mail.outbox[0].to


def test_muted_member_is_not_emailed(admin, member, tenant, auth):
    member.email = "member@example.ir"
    member.save(update_fields=["email"])
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member", muted=True)
    mail.outbox.clear()
    _post(auth(admin, tenant), f"/groups/{g.id}/messages",
          {"text": "@عضو", "mentions": [str(member.id)]})
    assert mail.outbox == []
