import json

from django.test import Client

from apps.social.models import Group, GroupMembership


def _group(tenant, admin):
    g = Group.objects.create(tenant=tenant, owner=admin, name="گروه", privacy="public")
    GroupMembership.objects.create(tenant=tenant, group=g, user=admin, role="owner", is_moderator=True)
    return g


def test_unread_counts_only_others_messages_and_clears_on_read(admin, member, tenant, auth):
    g = _group(tenant, admin)
    GroupMembership.objects.create(tenant=tenant, group=g, user=member, role="member")
    Client().post(f"/api/v1/groups/{g.id}/messages", json.dumps({"text": "۱"}),
                  content_type="application/json", **auth(admin, tenant))

    def unread_for(user):
        rows = Client().get("/api/v1/groups", **auth(user, tenant)).json()["data"]
        return [x for x in rows if x["id"] == str(g.id)][0]["unread"]

    assert unread_for(member) == 1
    assert unread_for(admin) == 0            # your own message is never unread
    Client().get(f"/api/v1/groups/{g.id}/messages", **auth(member, tenant))
    assert unread_for(member) == 0           # opening the conversation marks it read


def test_group_poll_is_scoped_to_its_group(admin, tenant, auth):
    g = _group(tenant, admin)
    other = Group.objects.create(tenant=tenant, owner=admin, name="دیگر", privacy="public")
    Client().post("/api/v1/polls", json.dumps({"question": "کِی؟", "option_labels": ["الف", "ب"], "group": str(g.id)}),
                  content_type="application/json", **auth(admin, tenant))
    assert Client().get(f"/api/v1/polls?group={g.id}", **auth(admin, tenant)).json()["meta"]["count"] == 1
    assert Client().get(f"/api/v1/polls?group={other.id}", **auth(admin, tenant)).json()["meta"]["count"] == 0
