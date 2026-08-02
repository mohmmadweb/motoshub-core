import json

from django.test import Client

from apps.chat.models import Channel, Message


def test_reaction_toggle(admin, tenant, auth):
    ch = Channel.objects.create(tenant=tenant, name="عمومی", owner=admin)
    msg = Message.objects.create(tenant=tenant, channel=ch, author=admin, text="سلام")
    url = f"/api/v1/chat/messages/{msg.id}/react"
    on = Client().post(url, json.dumps({"icon": "Heart"}), content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert on["reactions"] == [{"icon": "Heart", "count": 1, "reactedByMe": True}]
    off = Client().post(url, json.dumps({"icon": "Heart"}), content_type="application/json", **auth(admin, tenant)).json()["data"]
    assert off["reactions"] == []


def test_invalid_icon_rejected(admin, tenant, auth):
    ch = Channel.objects.create(tenant=tenant, name="ع", owner=admin)
    msg = Message.objects.create(tenant=tenant, channel=ch, author=admin, text="م")
    r = Client().post(f"/api/v1/chat/messages/{msg.id}/react", json.dumps({"icon": "Nope"}),
                      content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 422
