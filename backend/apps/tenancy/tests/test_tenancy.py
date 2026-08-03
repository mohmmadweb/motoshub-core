import json

from django.test import Client

from apps.tenancy.models import Company, Holding


def test_current_tenant_and_branding_update(admin, tenant, auth):
    d = Client().get("/api/v1/tenant", **auth(admin, tenant)).json()["data"]
    assert d["name"] == tenant.name and d["domain"] == tenant.domain

    r = Client().patch("/api/v1/tenant", json.dumps({"name": "نام تازه", "logo_color": "#0d9488"}),
                       content_type="application/json", **auth(admin, tenant))
    assert r.status_code == 200 and r.json()["data"]["name"] == "نام تازه"
    tenant.refresh_from_db()
    assert tenant.logo_color == "#0d9488"


def test_member_cannot_rebrand(member, tenant, auth):
    r = Client().patch("/api/v1/tenant", json.dumps({"name": "هک"}),
                       content_type="application/json", **auth(member, tenant))
    assert r.status_code == 403


def test_holdings_carry_their_companies(admin, tenant, auth):
    h = Holding.objects.create(tenant=tenant, name="هلدینگ الف")
    Company.objects.create(tenant=tenant, holding=h, name="شرکت ۱")
    d = Client().get("/api/v1/holdings", **auth(admin, tenant)).json()["data"]
    assert d[0]["name"] == "هلدینگ الف" and d[0]["companies"][0]["name"] == "شرکت ۱"


def test_public_tenants_needs_no_auth(tenant):
    d = Client().get("/api/v1/public/tenants").json()["data"]
    assert any(t["name"] == tenant.name for t in d)
