"""Thumbnail generation for uploaded images.

The admin console offers «بازسازی بندانگشتی‌ها». For that to mean anything the
platform has to produce thumbnails in the first place, which it previously did
not — the button had nothing to rebuild.

Thumbnails are written next to the original as JPEG, since a preview does not
need transparency and JPEG keeps the file small. Failure is never fatal: an
image the decoder cannot read simply ends up without a preview rather than
breaking the upload that carried it.
"""
import io
import logging

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

THUMB_SIZE = (400, 400)
IMAGE_KINDS = {"photo"}


def build_thumbnail(attachment) -> bool:
    """Generate (or replace) this attachment's thumbnail. True if one now exists."""
    if attachment.kind not in IMAGE_KINDS or not attachment.file:
        return False
    try:
        from PIL import Image, ImageOps
    except ImportError:                       # pragma: no cover - Pillow is a dependency
        logger.warning("Pillow is unavailable; thumbnails cannot be generated.")
        return False

    try:
        attachment.file.open("rb")
        with Image.open(attachment.file) as img:
            # EXIF orientation first, or portrait photos come out sideways.
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82, optimize=True)
    except Exception as exc:                  # noqa: BLE001 - any decode failure
        logger.info("thumbnail skipped for %s: %s", attachment.pk, exc)
        return False
    finally:
        attachment.file.close()

    stem = attachment.name.rsplit(".", 1)[0][:80] or "thumb"
    attachment.thumbnail.save(f"{stem}.jpg", ContentFile(buf.getvalue()), save=False)
    attachment.save(update_fields=["thumbnail"])
    return True


def rebuild_all(tenant, only_missing: bool = False) -> dict:
    """Rebuild thumbnails for a tenant's images. Returns a small tally."""
    from .models import Attachment

    qs = Attachment.objects.filter(tenant=tenant, kind__in=IMAGE_KINDS)
    if only_missing:
        qs = qs.filter(thumbnail="")
    built = failed = 0
    for att in qs.iterator():
        if build_thumbnail(att):
            built += 1
        else:
            failed += 1
    return {"built": built, "failed": failed, "total": built + failed}
