"""Thumbnail generation and the console's rebuild action."""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from apps.core.models import Attachment
from apps.core.thumbnails import build_thumbnail, rebuild_all


def _png(size=(900, 600), colour=(30, 90, 160)) -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", size, colour).save(buf, format="PNG")
    return buf.getvalue()


def _upload(headers, name, data, content_type):
    return Client().post(
        "/api/v1/uploads",
        {"file": SimpleUploadedFile(name, data, content_type=content_type)},
        **headers,
    )


@pytest.mark.django_db
def test_uploading_an_image_produces_a_thumbnail(admin, tenant, auth):
    res = _upload(auth(admin, tenant), "photo.png", _png(), "image/png")
    assert res.status_code == 201
    body = res.json()["data"]
    assert body["thumbnail_url"], "an uploaded image should come back with a preview"

    att = Attachment.objects.get(id=body["id"])
    from PIL import Image

    with Image.open(att.thumbnail) as thumb:
        # Scaled down, aspect preserved, and never enlarged.
        assert max(thumb.size) <= 400
        assert thumb.size[0] > thumb.size[1]


@pytest.mark.django_db
def test_documents_get_no_thumbnail(admin, tenant, auth):
    res = _upload(auth(admin, tenant), "notes.txt", b"hello", "text/plain")
    assert res.status_code == 201
    assert res.json()["data"]["thumbnail_url"] == ""


@pytest.mark.django_db
def test_a_corrupt_image_does_not_break_the_upload(admin, tenant, auth):
    """A file that claims to be a PNG but is not still uploads — it simply has
    no preview. Losing the file because its preview failed would be worse."""
    res = _upload(auth(admin, tenant), "broken.png", b"not really a png", "image/png")
    assert res.status_code == 201
    assert res.json()["data"]["thumbnail_url"] == ""


@pytest.mark.django_db
def test_rebuild_regenerates_previews(admin, tenant, auth):
    _upload(auth(admin, tenant), "a.png", _png(), "image/png")
    _upload(auth(admin, tenant), "b.png", _png((300, 300)), "image/png")

    # Wipe the previews as if the size setting had changed.
    Attachment.objects.filter(tenant=tenant, kind="photo").update(thumbnail="")
    assert not any(a.thumbnail for a in Attachment.objects.filter(tenant=tenant, kind="photo"))

    tally = rebuild_all(tenant)
    assert tally == {"built": 2, "failed": 0, "total": 2}
    assert all(a.thumbnail for a in Attachment.objects.filter(tenant=tenant, kind="photo"))


@pytest.mark.django_db
def test_rebuild_endpoint_needs_the_storage_permission(admin, member, platform_admin, tenant, auth):
    _upload(auth(admin, tenant), "a.png", _png(), "image/png")
    # settings.storage belongs to راهبر پلتفرم alone — an org admin is refused.
    assert Client().post("/api/v1/settings/storage/thumbnails", **auth(member, tenant)).status_code == 403
    assert Client().post("/api/v1/settings/storage/thumbnails", **auth(admin, tenant)).status_code == 403

    res = Client().post("/api/v1/settings/storage/thumbnails", **auth(platform_admin, tenant))
    assert res.status_code == 200
    assert res.json()["data"]["built"] == 1


@pytest.mark.django_db
def test_rebuild_can_fill_only_the_gaps(admin, tenant, auth):
    _upload(auth(admin, tenant), "kept.png", _png(), "image/png")
    _upload(auth(admin, tenant), "lost.png", _png(), "image/png")
    lost = Attachment.objects.filter(tenant=tenant, name="lost.png").first()
    lost.thumbnail = ""
    lost.save(update_fields=["thumbnail"])

    assert rebuild_all(tenant, only_missing=True)["total"] == 1


@pytest.mark.django_db
def test_thumbnail_respects_exif_orientation(admin, tenant, auth):
    """A portrait photo tagged sideways must not come back rotated."""
    from PIL import Image

    buf = io.BytesIO()
    img = Image.new("RGB", (200, 400), (10, 10, 10))
    exif = img.getexif()
    exif[274] = 6                      # orientation: rotate 90°
    img.save(buf, format="JPEG", exif=exif)

    res = _upload(auth(admin, tenant), "portrait.jpg", buf.getvalue(), "image/jpeg")
    att = Attachment.objects.get(id=res.json()["data"]["id"])
    assert build_thumbnail(att) or att.thumbnail
    with Image.open(att.thumbnail) as thumb:
        # After transposition the 200×400 image is 400×200.
        assert thumb.size[0] > thumb.size[1]
