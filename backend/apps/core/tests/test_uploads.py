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
    big = b"x" * (uploads.MAX_BYTES + 1)
    assert _upload(auth(admin, tenant), "big.pdf", big, "application/pdf").status_code == 413
