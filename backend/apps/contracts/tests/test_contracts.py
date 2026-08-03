import json
from django.test import Client


def _post(path, body, admin, tenant, auth):
    return Client().post(f"/api/v1/{path}", json.dumps(body), content_type="application/json", **auth(admin, tenant))


def test_contract_create_and_advance(admin, tenant, auth):
    c = _post("contracts", {"title": "قرارداد نمونه", "vendor": "شرکت الف"}, admin, tenant, auth).json()["data"]
    assert c["stage"] == "negotiation"
    r = Client().post(f"/api/v1/contracts/{c['id']}/advance", **auth(admin, tenant))
    assert r.status_code == 200 and r.json()["data"]["stage"] == "rfp"


def test_rich_contract_submodules(admin, tenant, auth):
    assert _post("contracts/tech-transfer", {"title": "تبادل", "company": "ب"}, admin, tenant, auth).status_code == 201
    assert _post("contracts/tenders", {"title": "مناقصه", "method": "public", "stage": "publish"}, admin, tenant, auth).status_code == 201
    assert _post("contracts/esign", {"title": "سند", "kind": "nf"}, admin, tenant, auth).status_code == 201
