"""Real storage figures for the admin console's «فضای ذخیره‌سازی» section.

Everything here is measured, not estimated: category sizes come from the
Attachment rows, disk capacity from the filesystem holding MEDIA_ROOT, and the
database size from Postgres itself. The panel previously showed hardcoded
numbers, which is worse than showing nothing — an operator would plan against
figures that were never true.
"""
import os
import shutil

from django.conf import settings
from django.db import connection
from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Attachment

GB = 1024 ** 3

# Colour per kind so the stacked bar keeps a stable legend.
KIND_META = {
    "doc": ("پیوست‌ها و اسناد", "bg-brand-600"),
    "photo": ("تصاویر و آواتارها", "bg-emerald-500"),
    "video": ("ویدئو و رسانه", "bg-navy-700"),
    "audio": ("پیام‌های صوتی", "bg-amber-500"),
    "other": ("سایر فایل‌ها", "bg-rose-500"),
}


def _gb(n_bytes: int) -> float:
    return round((n_bytes or 0) / GB, 2)


class StorageUsageView(APIView):
    """GET → measured usage. POST → remove Attachment rows whose file is gone."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request, "tenant", None)
        rows = Attachment.objects.filter(tenant=tenant)

        by_kind = rows.values("kind").annotate(bytes=Sum("size"), files=Count("id"))
        seen = {r["kind"]: r for r in by_kind}
        categories = [
            {
                "kind": kind,
                "label": label,
                "color": color,
                "sizeGb": _gb(seen.get(kind, {}).get("bytes", 0)),
                "files": seen.get(kind, {}).get("files", 0),
            }
            for kind, (label, color) in KIND_META.items()
        ]

        # Whoever has uploaded the most — the actionable version of «پرمصرف‌ترین‌ها».
        top = (
            rows.exclude(uploaded_by=None)
            .values("uploaded_by__id", "uploaded_by__name")
            .annotate(bytes=Sum("size"), files=Count("id"))
            .order_by("-bytes")[:5]
        )
        top_consumers = [
            {
                "id": str(t["uploaded_by__id"]),
                "name": t["uploaded_by__name"] or "—",
                "type": "کاربر",
                "sizeGb": _gb(t["bytes"]),
                "files": t["files"],
            }
            for t in top
        ]

        media_root = str(settings.MEDIA_ROOT)
        os.makedirs(media_root, exist_ok=True)
        disk = shutil.disk_usage(media_root)

        db_bytes = 0
        if connection.vendor == "postgresql":
            with connection.cursor() as cur:
                cur.execute("SELECT pg_database_size(current_database())")
                db_bytes = cur.fetchone()[0]

        orphans = sum(
            1 for a in rows.only("file")
            if not a.file or not os.path.exists(os.path.join(media_root, a.file.name))
        )

        return Response({
            "disk_total_gb": _gb(disk.total),
            "disk_used_gb": _gb(disk.used),
            "disk_free_gb": _gb(disk.free),
            "attachments_gb": _gb(rows.aggregate(n=Sum("size"))["n"] or 0),
            "attachments_files": rows.count(),
            "database_gb": _gb(db_bytes),
            "categories": categories,
            "top_consumers": top_consumers,
            "orphan_records": orphans,
        })

    def post(self, request):
        """Drop rows whose underlying file no longer exists.

        Deliberately never deletes a file from disk — the only thing removed is
        a database row already pointing at nothing, so no content can be lost.
        """
        tenant = getattr(request, "tenant", None)
        media_root = str(settings.MEDIA_ROOT)
        stale = [
            a.id for a in Attachment.objects.filter(tenant=tenant).only("file")
            if not a.file or not os.path.exists(os.path.join(media_root, a.file.name))
        ]
        Attachment.objects.filter(id__in=stale).delete()
        return Response({"removed": len(stale)})
