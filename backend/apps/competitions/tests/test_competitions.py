import json

from django.test import Client

from apps.competitions.models import Challenge, Competition, CompetitionEntry


def test_vote_toggle(admin, tenant, auth):
    comp = Competition.objects.create(tenant=tenant, title="مسابقه", status="open")
    entry = CompetitionEntry.objects.create(tenant=tenant, competition=comp, by="کاربر", title="اثر")
    r1 = Client().post(f"/api/v1/competitions/vote?entry={entry.id}", **auth(admin, tenant)).json()["data"]
    assert r1 == {"votes": 1, "my_vote": True}
    r2 = Client().post(f"/api/v1/competitions/vote?entry={entry.id}", **auth(admin, tenant)).json()["data"]
    assert r2 == {"votes": 0, "my_vote": False}


def test_challenge_join_toggle(admin, tenant, auth):
    ch = Challenge.objects.create(tenant=tenant, title="چالش", kind="collective", status="active")
    r1 = Client().post(f"/api/v1/challenges/{ch.id}/join", **auth(admin, tenant)).json()["data"]
    assert r1 == {"joined": 1, "is_joined": True}
    r2 = Client().post(f"/api/v1/challenges/{ch.id}/join", **auth(admin, tenant)).json()["data"]
    assert r2 == {"joined": 0, "is_joined": False}


def test_competition_list_includes_entries_and_my_vote(admin, tenant, auth):
    comp = Competition.objects.create(tenant=tenant, title="م۲", status="open")
    CompetitionEntry.objects.create(tenant=tenant, competition=comp, by="ب", title="ت")
    data = Client().get("/api/v1/competitions", **auth(admin, tenant)).json()["data"]
    assert data[0]["entries"][0]["my_vote"] is False and data[0]["entries"][0]["votes"] == 0
