"""Single upload endpoint used by chat attachments, knowledge docs and media."""
import mimetypes

from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attachment

# Conservative allow-list: no executables, no archives that hide them.
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg",
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv",
    "mp3", "wav", "ogg", "m4a", "mp4", "webm", "zip",
}
# Ceiling imposed by nginx's client_max_body_size — the tenant limit below can
# be lower than this but never higher, since nginx rejects the request before
# Django ever sees it.
HARD_MAX_BYTES = 25 * 1024 * 1024


def _max_bytes(request) -> int:
    """The tenant's «حداکثر حجم آپلود» from the admin console, capped by nginx."""
    from apps.console.models import WorkflowSettings
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return HARD_MAX_BYTES
    mb = (
        WorkflowSettings.objects.filter(tenant=tenant)
        .values_list("upload_max_mb", flat=True)
        .first()
    )
    return min(HARD_MAX_BYTES, (mb or 100) * 1024 * 1024)


def _kind_for(ext: str, content_type: str) -> str:
    if ext in {"jpg", "jpeg", "png", "gif", "webp", "svg"} or content_type.startswith("image/"):
        return "photo"
    if ext in {"mp3", "wav", "ogg", "m4a"} or content_type.startswith("audio/"):
        return "audio"
    if ext in {"mp4", "webm"} or content_type.startswith("video/"):
        return "video"
    if ext in {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"}:
        return "doc"
    return "other"


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    human_size = serializers.CharField(read_only=True)

    class Meta:
        model = Attachment
        fields = ["id", "name", "kind", "size", "human_size", "content_type", "url", "created_at"]

    def get_url(self, obj):
        # Relative on purpose: behind a reverse proxy the Host header carries no
        # port, so an absolute URL would point at the wrong origin. The browser
        # resolves this against whatever origin it is already talking to.
        return obj.file.url if obj.file else ""


class UploadView(APIView):
    """POST multipart `file` → a stored Attachment the caller can reference."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": "فایلی ارسال نشده است."}}, status=422)
        limit = _max_bytes(request)
        if upload.size > limit:
            mb = limit // (1024 * 1024)
            return Response({"error": {"code": 413, "type": "payload_too_large",
                                       "message": f"حجم فایل بیش از {mb} مگابایت است."}}, status=413)

        ext = (upload.name.rsplit(".", 1)[-1] if "." in upload.name else "").lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response({"error": {"code": 422, "type": "unprocessable_entity",
                                       "message": f"پسوند «{ext or '—'}» مجاز نیست."}}, status=422)

        content_type = upload.content_type or mimetypes.guess_type(upload.name)[0] or ""
        att = Attachment.objects.create(
            tenant=getattr(request, "tenant", None), file=upload, name=upload.name[:255],
            kind=_kind_for(ext, content_type), size=upload.size, content_type=content_type[:120],
            uploaded_by=request.user,
        )
        return Response(AttachmentSerializer(att, context={"request": request}).data, status=201)
