"""Blocking, direct-message attachments, and call records."""
import json

import pytest
from django.test import Client

from apps.chat.models import Call, DirectMessage, UserBlock


def _post(path, payload, headers):
    return Client().post(path, json.dumps(payload), content_type="application/json", **headers)


def _patch(path, payload, headers):
    return Client().patch(path, json.dumps(payload), content_type="application/json", **headers)


@pytest.mark.django_db
def test_blocking_stops_messages_in_both_directions(admin, member, tenant, auth):
    a, m = auth(admin, tenant), auth(member, tenant)

    # Before the block, the conversation works.
    assert _post("/api/v1/chat/dms", {"to": str(member.id), "text": "سلام"}, a).status_code == 201

    assert Client().put(f"/api/v1/chat/blocks/{member.id}", **a).status_code == 200

    # The blocker cannot send…
    assert _post("/api/v1/chat/dms", {"to": str(member.id), "text": "باز هم"}, a).status_code == 403
    # …and the blocked person cannot send back, or the block would be one-way
    # and the blocker would keep receiving what they asked not to.
    assert _post("/api/v1/chat/dms", {"to": str(admin.id), "text": "چرا؟"}, m).status_code == 403

    assert Client().delete(f"/api/v1/chat/blocks/{member.id}", **a).status_code == 200
    assert _post("/api/v1/chat/dms", {"to": str(member.id), "text": "دوباره"}, a).status_code == 201


@pytest.mark.django_db
def test_block_list_reports_who_i_blocked(admin, member, tenant, auth):
    a = auth(admin, tenant)
    Client().put(f"/api/v1/chat/blocks/{member.id}", **a)
    rows = Client().get("/api/v1/chat/blocks", **a).json()["data"]
    assert [r["id"] for r in rows] == [str(member.id)]


@pytest.mark.django_db
def test_blocking_yourself_is_refused(admin, tenant, auth):
    assert Client().put(f"/api/v1/chat/blocks/{admin.id}", **auth(admin, tenant)).status_code == 422


@pytest.mark.django_db
def test_shared_media_lists_only_files(admin, member, tenant, auth):
    a = auth(admin, tenant)
    _post("/api/v1/chat/dms", {"to": str(member.id), "text": "فقط متن"}, a)
    _post("/api/v1/chat/dms", {
        "to": str(member.id), "text": "",
        "attachment": {"url": "/media/uploads/x.png", "name": "x.png", "kind": "photo", "size": 10},
    }, a)

    rows = Client().get(f"/api/v1/chat/dms/{member.id}/media", **a).json()["data"]
    assert len(rows) == 1
    assert rows[0]["name"] == "x.png"


@pytest.mark.django_db
def test_a_message_needs_text_or_a_file(admin, member, tenant, auth):
    assert _post("/api/v1/chat/dms", {"to": str(member.id), "text": ""}, auth(admin, tenant)).status_code == 422


@pytest.mark.django_db
def test_call_is_recorded_and_timed(admin, member, tenant, auth):
    a, m = auth(admin, tenant), auth(member, tenant)

    placed = _post("/api/v1/chat/calls", {"to": str(member.id), "kind": "video"}, a)
    assert placed.status_code == 201
    call_id = placed.json()["data"]["id"]
    assert Call.objects.get(id=call_id).status == "ringing"

    # The callee answers, then either side hangs up.
    assert _patch(f"/api/v1/chat/calls/{call_id}", {"status": "accepted"}, m).status_code == 200
    ended = _patch(f"/api/v1/chat/calls/{call_id}", {"status": "ended"}, a)
    assert ended.status_code == 200
    assert ended.json()["data"]["status"] == "ended"

    call = Call.objects.get(id=call_id)
    assert call.started_at is not None and call.ended_at is not None

    # Both sides see it in their history, from their own perspective.
    assert Client().get("/api/v1/chat/calls", **a).json()["data"][0]["direction"] == "out"
    assert Client().get("/api/v1/chat/calls", **m).json()["data"][0]["direction"] == "in"


@pytest.mark.django_db
def test_a_stranger_cannot_change_someone_elses_call(admin, member, tenant, auth, django_user_model):
    outsider = django_user_model.objects.create_user(
        username="outsider", password="x", name="بیرونی", tenant=tenant,
    )
    call = Call.objects.create(tenant=tenant, caller=admin, callee=member, kind="audio")
    assert _patch(f"/api/v1/chat/calls/{call.id}", {"status": "ended"}, auth(outsider, tenant)).status_code == 404


@pytest.mark.django_db
def test_calling_a_blocked_user_is_refused(admin, member, tenant, auth):
    UserBlock.objects.create(tenant=tenant, user=member, blocked=admin)
    assert _post("/api/v1/chat/calls", {"to": str(member.id), "kind": "audio"}, auth(admin, tenant)).status_code == 403


@pytest.mark.django_db
def test_clearing_a_thread_removes_it_for_good(admin, member, tenant, auth):
    a = auth(admin, tenant)
    _post("/api/v1/chat/dms", {"to": str(member.id), "text": "یک"}, a)
    _post("/api/v1/chat/dms", {"to": str(member.id), "text": "دو"}, a)
    assert Client().delete(f"/api/v1/chat/dms/{member.id}", **a).json()["data"]["deleted"] == 2
    assert DirectMessage.objects.filter(sender=admin, recipient=member).count() == 0
