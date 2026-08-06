from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client


def _upload(auth_headers, name, content=b"hello", content_type="text/plain"):
    return Client().post("/api/v1/uploads",
                         {"file": SimpleUploadedFile(name, content, content_type=content_type)},
                         **auth_headers)


def test_upload_stores_and_classifies(admin, tenant, auth):
    r = _upload(auth(admin, tenant), "گزارش.txt")
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["kind"] == "doc" and d["name"] == "گزارش.txt" and d["url"]


def test_images_are_classified_as_photos(admin, tenant, auth):
    d = _upload(auth(admin, tenant), "pic.png", b"\x89PNG\r\n", "image/png").json()["data"]
    assert d["kind"] == "photo"


def test_executable_extensions_are_rejected(admin, tenant, auth):
    assert _upload(auth(admin, tenant), "evil.sh", b"#!/bin/sh").status_code == 422
    assert _upload(auth(admin, tenant), "evil.exe", b"MZ").status_code == 422


def test_upload_requires_a_file_and_authentication(admin, tenant, auth):
    assert Client().post("/api/v1/uploads", {}, **auth(admin, tenant)).status_code == 422
    assert Client().post("/api/v1/uploads", {}).status_code == 401


def test_oversized_upload_is_rejected(admin, tenant, auth, settings):
    from apps.core import uploads
    big = b"x" * (uploads.HARD_MAX_BYTES + 1)
    assert _upload(auth(admin, tenant), "big.pdf", big, "application/pdf").status_code == 413


def test_upload_limit_follows_the_tenant_setting(admin, tenant, auth):
    """The console's «حداکثر حجم آپلود» is enforced, not decorative."""
    from apps.console.models import WorkflowSettings

    WorkflowSettings.objects.update_or_create(tenant=tenant, defaults={"upload_max_mb": 1})
    two_mb = b"x" * (2 * 1024 * 1024)
    assert _upload(auth(admin, tenant), "big.pdf", two_mb, "application/pdf").status_code == 413

    half_mb = b"x" * (512 * 1024)
    assert _upload(auth(admin, tenant), "ok.pdf", half_mb, "application/pdf").status_code == 201


def test_maintenance_mode_refuses_writes_but_allows_reads(admin, member, tenant, auth):
    """The switch in «متغیرهای سیستم» actually closes the platform."""
    from apps.console.models import WorkflowSettings

    WorkflowSettings.objects.update_or_create(tenant=tenant, defaults={"maintenance_mode": True})
    c = Client()
    # A plain member can still read…
    assert c.get("/api/v1/news", **auth(member, tenant)).status_code == 200
    # …but cannot write.
    assert c.post(
        "/api/v1/news", {"title": "x", "summary": "y"},
        content_type="application/json", **auth(member, tenant),
    ).status_code == 403
