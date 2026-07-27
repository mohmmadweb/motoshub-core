"""
Unified HS256 JWT — signed with OW_PASSWORD_PEPPER so tokens interoperate with
the PHP/Oxwall backend behind the Kong gateway.

Claims: {iat, exp, sub, iss, typ, tid}. `sub` is the user id (string); `tid` is
the active tenant id. The PHP backend issues the same {iat, exp, sub} core.
"""
import jwt
from django.conf import settings
from django.utils import timezone


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.OW_PASSWORD_PEPPER, algorithm=settings.JWT_ALGORITHM)


def issue_access(user, tenant_id=None) -> str:
    now = timezone.now()
    return _encode(
        {
            "typ": "access",
            "sub": str(user.id),
            "tid": str(tenant_id or user.tenant_id or ""),
            "iss": settings.JWT_ISSUER,
            "iat": int(now.timestamp()),
            "exp": int((now + settings.JWT_ACCESS_TTL).timestamp()),
        }
    )


def issue_refresh(user) -> str:
    now = timezone.now()
    return _encode(
        {
            "typ": "refresh",
            "sub": str(user.id),
            "iss": settings.JWT_ISSUER,
            "iat": int(now.timestamp()),
            "exp": int((now + settings.JWT_REFRESH_TTL).timestamp()),
        }
    )


def decode(token: str) -> dict:
    """Raises jwt.InvalidTokenError (incl. ExpiredSignatureError) on failure."""
    return jwt.decode(token, settings.OW_PASSWORD_PEPPER, algorithms=[settings.JWT_ALGORITHM])


def issue_pair(user, tenant_id=None) -> dict:
    return {"access": issue_access(user, tenant_id), "refresh": issue_refresh(user)}
