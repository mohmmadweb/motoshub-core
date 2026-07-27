"""DRF authentication for the unified HS256 JWT."""
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User
from .tokens import decode


class UnifiedJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith(self.keyword + " "):
            return None
        token = header[len(self.keyword) + 1:].strip()
        try:
            payload = decode(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("توکن منقضی شده است.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("توکن نامعتبر است.")

        if payload.get("typ") not in (None, "access"):
            raise AuthenticationFailed("نوع توکن نامعتبر است.")

        try:
            user = User.objects.select_related("tenant", "company").get(id=payload["sub"], is_active=True)
        except (User.DoesNotExist, KeyError):
            raise AuthenticationFailed("کاربر یافت نشد.")

        # Stash the token's tenant claim for the tenant middleware.
        request.jwt_tenant_id = payload.get("tid") or None
        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
