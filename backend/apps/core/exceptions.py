"""
Uniform error body (shared contract): 401 / 403 / 404 / 422 (+ others) all
return

    { "error": { "code": <http-status>, "type": "<slug>", "message": "<fa>",
                 "details": {<field: [msgs]>} } }

DRF's ValidationError (normally 400) is remapped to 422 to match the contract.
"""
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

TYPE_BY_STATUS = {
    400: "bad_request",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    422: "unprocessable_entity",
    429: "throttled",
    500: "server_error",
}


def envelope_exception_handler(exc, context):
    # ValidationError → 422 (contract), not the DRF default 400.
    if isinstance(exc, ValidationError):
        return _build(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.detail, "اعتبارسنجی داده ناموفق بود.")

    response = drf_exception_handler(exc, context)
    if response is None:
        # Unhandled: let DEBUG surface the traceback; otherwise a clean 500.
        if isinstance(exc, Http404):
            return _build(404, None, "یافت نشد.")
        if isinstance(exc, PermissionDenied):
            return _build(403, None, "دسترسی مجاز نیست.")
        return None

    code = response.status_code
    detail = response.data
    message = _message_from(detail, code)
    details = detail if isinstance(detail, dict) and "detail" not in detail else None
    return _build(code, details, message)


def _message_from(detail, code):
    if isinstance(detail, dict) and "detail" in detail:
        return str(detail["detail"])
    if isinstance(detail, (list, tuple)) and detail:
        return str(detail[0])
    return {
        401: "احراز هویت لازم است.",
        403: "دسترسی مجاز نیست.",
        404: "یافت نشد.",
        405: "متد مجاز نیست.",
        429: "تعداد درخواست‌ها بیش از حد مجاز است.",
    }.get(code, "خطایی رخ داد.")


def _build(code, details, message):
    body = {
        "error": {
            "code": code,
            "type": TYPE_BY_STATUS.get(code, "error"),
            "message": message,
        }
    }
    if details:
        body["error"]["details"] = details
    return Response(body, status=code)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "تعارض وضعیت."
    default_code = "conflict"
