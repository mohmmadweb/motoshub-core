"""WebRTC signalling relay on the DM socket.

Media never reaches the server, so what matters here is that the relay carries
the handshake to the right person and refuses to carry it for anyone else.
"""
import pytest
from channels.testing import WebsocketCommunicator

from apps.accounts.tokens import issue_access
from apps.chat.models import Call
from config.asgi import application


async def _connect(user, tenant):
    token = issue_access(user, tenant.id)
    comm = WebsocketCommunicator(application, f"/ws/dm/?token={token}")
    connected, _ = await comm.connect()
    assert connected
    return comm


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_signalling_reaches_the_other_participant(admin, member, tenant):
    from channels.db import database_sync_to_async

    call = await database_sync_to_async(Call.objects.create)(
        tenant=tenant, caller=admin, callee=member, kind="audio",
    )
    caller = await _connect(admin, tenant)
    callee = await _connect(member, tenant)

    offer = {"sdp": {"type": "offer", "sdp": "v=0..."}}
    await caller.send_json_to({
        "type": "call:signal", "to": str(member.id), "callId": str(call.id), "signal": offer,
    })

    got = await callee.receive_json_from(timeout=3)
    assert got["type"] == "call:signal"
    assert got["callId"] == str(call.id)
    # The sender is stamped by the server, not taken from the payload.
    assert got["from"] == str(admin.id)
    assert got["signal"] == offer

    await caller.disconnect()
    await callee.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_an_outsider_cannot_inject_signalling(admin, member, tenant, django_user_model):
    """Someone not on the call must not be able to push SDP into it — that
    would let a third party hijack the negotiation."""
    from channels.db import database_sync_to_async

    outsider = await database_sync_to_async(django_user_model.objects.create_user)(
        username="lurker", password="x", name="ناظر", tenant=tenant,
    )
    call = await database_sync_to_async(Call.objects.create)(
        tenant=tenant, caller=admin, callee=member, kind="audio",
    )

    intruder = await _connect(outsider, tenant)
    callee = await _connect(member, tenant)

    await intruder.send_json_to({
        "type": "call:signal", "to": str(member.id), "callId": str(call.id),
        "signal": {"sdp": {"type": "offer", "sdp": "malicious"}},
    })

    assert await callee.receive_nothing(timeout=1.5), "an outsider's signalling must be dropped"

    await intruder.disconnect()
    await callee.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_typing_is_relayed_with_the_senders_identity(admin, member, tenant):
    a = await _connect(admin, tenant)
    b = await _connect(member, tenant)

    # Claiming to be someone else is ignored: the server uses the socket's user.
    await a.send_json_to({"type": "typing", "to": str(member.id), "from": "spoofed"})

    got = await b.receive_json_from(timeout=3)
    assert got == {"type": "typing", "from": str(admin.id)}

    await a.disconnect()
    await b.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_a_bad_call_id_is_ignored_not_fatal(admin, member, tenant):
    a = await _connect(admin, tenant)
    b = await _connect(member, tenant)

    await a.send_json_to({
        "type": "call:signal", "to": str(member.id), "callId": "not-a-uuid",
        "signal": {"sdp": {"type": "offer", "sdp": "x"}},
    })
    assert await b.receive_nothing(timeout=1.5)

    # The socket is still usable afterwards.
    await a.send_json_to({"type": "typing", "to": str(member.id)})
    assert (await b.receive_json_from(timeout=3))["type"] == "typing"

    await a.disconnect()
    await b.disconnect()
