from django.test import Client

from apps.projects.models import Project


def test_csv_export_has_bom_and_rows(admin, tenant, auth):
    Project.objects.create(tenant=tenant, name="پ۱", health="green")
    Project.objects.create(tenant=tenant, name="پ۲", health="red")
    r = Client().get("/api/v1/reports/export?dimension=projects_by_health", **auth(admin, tenant))
    assert r.status_code == 200
    assert r["Content-Type"].startswith("text/csv")
    assert "attachment" in r["Content-Disposition"]
    body = r.content.decode("utf-8")
    assert body.startswith("﻿")           # Excel needs the BOM for Persian
    assert "سبز" in body and "قرمز" in body and "مجموع" in body


def test_invalid_dimension_is_rejected(admin, tenant, auth):
    assert Client().get("/api/v1/reports/export?dimension=bogus", **auth(admin, tenant)).status_code == 422


def test_export_needs_permission(member, tenant, auth):
    assert Client().get("/api/v1/reports/export?dimension=projects_by_health",
                        **auth(member, tenant)).status_code == 403
