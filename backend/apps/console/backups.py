"""Manual database backups from the admin console.

The scheduled `backup` container keeps its own copies on its own volume, which
the API cannot see. The console's «پشتیبان‌گیری دستی» therefore needs its own
directory — BACKUP_DIR, shared with the API container — so that a backup taken
from the panel is a real file an administrator can list and download.

The dump is written to a `.part` name and renamed on success, so a half-written
file is never mistaken for a usable backup.
"""
import logging
import os
import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/app/backups"))
# Guards the download path: only files this module could have written.
NAME_RE = re.compile(r"^motoshub-\d{8}-\d{6}\.sql\.gz$")


def _human(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _require_backup_perm(request) -> bool:
    user = request.user
    if getattr(user, "is_superuser", False):
        return True
    return "settings.storage" in user.get_permission_ids(getattr(request, "tenant", None))


def _listing() -> list[dict]:
    if not BACKUP_DIR.exists():
        return []
    out = []
    for f in sorted(BACKUP_DIR.glob("motoshub-*.sql.gz"), reverse=True):
        stat = f.stat()
        out.append({
            "name": f.name,
            "size": stat.st_size,
            "human_size": _human(stat.st_size),
            "created_at": int(stat.st_mtime),
        })
    return out


class BackupView(APIView):
    """GET → the backups this panel has taken. POST → take one now."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require_backup_perm(request):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        return Response({"backups": _listing(), "directory": str(BACKUP_DIR)})

    def post(self, request):
        if not _require_backup_perm(request):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)

        from django.utils import timezone

        db = settings.DATABASES["default"]
        if "postgresql" not in db.get("ENGINE", ""):
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": "پشتیبان‌گیری فقط برای PostgreSQL در دسترس است."}}, status=422)

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        final = BACKUP_DIR / f"motoshub-{stamp}.sql.gz"
        partial = final.with_suffix(final.suffix + ".part")

        env = {**os.environ, "PGPASSWORD": db.get("PASSWORD") or ""}
        cmd = [
            "pg_dump",
            "-h", db.get("HOST") or "localhost",
            "-p", str(db.get("PORT") or 5432),
            "-U", db.get("USER") or "postgres",
            "-d", db.get("NAME") or "postgres",
            "--no-owner", "--no-privileges", "--compress=6",
        ]
        try:
            with partial.open("wb") as fh:
                proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.PIPE, env=env, timeout=600)
        except FileNotFoundError:
            return Response({"error": {"code": 500, "type": "server_error",
                                       "message": "ابزار pg_dump روی سرور در دسترس نیست."}}, status=500)
        except subprocess.TimeoutExpired:
            partial.unlink(missing_ok=True)
            return Response({"error": {"code": 504, "type": "timeout",
                                       "message": "پشتیبان‌گیری بیش از حد طول کشید."}}, status=504)

        if proc.returncode != 0 or partial.stat().st_size < 1024:
            detail = (proc.stderr or b"").decode("utf-8", "replace")[:200]
            logger.error("pg_dump failed: %s", detail)
            partial.unlink(missing_ok=True)
            return Response({"error": {"code": 500, "type": "server_error",
                                       "message": "پشتیبان‌گیری ناموفق بود."}}, status=500)

        partial.rename(final)     # only a complete dump ever gets the real name
        stat = final.stat()
        return Response({
            "name": final.name, "size": stat.st_size, "human_size": _human(stat.st_size),
            "created_at": int(stat.st_mtime),
        }, status=201)


class BackupDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, name=None):
        if not _require_backup_perm(request):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        # Reject anything that is not a name this module generates, so the
        # parameter can never walk out of the backup directory.
        if not name or not NAME_RE.match(name):
            return Response({"error": {"code": 404, "type": "not_found", "message": "پشتیبان یافت نشد."}}, status=404)
        path = BACKUP_DIR / name
        if not path.is_file():
            return Response({"error": {"code": 404, "type": "not_found", "message": "پشتیبان یافت نشد."}}, status=404)
        return FileResponse(path.open("rb"), as_attachment=True, filename=name)

    def delete(self, request, name=None):
        if not _require_backup_perm(request):
            return Response({"error": {"code": 403, "type": "forbidden", "message": "دسترسی لازم را ندارید."}}, status=403)
        if not name or not NAME_RE.match(name):
            return Response({"error": {"code": 404, "type": "not_found", "message": "پشتیبان یافت نشد."}}, status=404)
        (BACKUP_DIR / name).unlink(missing_ok=True)
        return Response(status=204)
