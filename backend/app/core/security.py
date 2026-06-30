"""Security primitives: password hashing and RS256 JWT handling.

Passwords are hashed with bcrypt. JSON Web Tokens are signed with the RSA
private key (RS256) and verified with the RSA public key, so the verifying
side never needs the signing secret.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

ALGORITHM = "RS256"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if ``plain_password`` matches the stored bcrypt hash."""
    return _password_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    """Return a SHA-256 hex digest of a token for safe at-rest storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@lru_cache
def _signing_key() -> str:
    """Return the cached RSA private key used to sign tokens."""
    return get_settings().read_private_key()


@lru_cache
def _verifying_key() -> str:
    """Return the cached RSA public key used to verify tokens."""
    return get_settings().read_public_key()


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """Build and sign a JWT for the given subject and type.

    Args:
        subject: The user identifier stored in the ``sub`` claim.
        token_type: Either ``access`` or ``refresh``.
        expires_delta: How long the token remains valid.

    Returns:
        The encoded, signed JWT string.
    """
    issued_at = datetime.now(timezone.utc)
    claims: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": issued_at,
        "exp": issued_at + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(claims, _signing_key(), algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    """Create a short-lived access token for the given subject."""
    settings = get_settings()
    return _create_token(
        subject, ACCESS_TOKEN_TYPE, timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token for the given subject."""
    settings = get_settings()
    return _create_token(
        subject, REFRESH_TOKEN_TYPE, timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Decode and validate a JWT, returning its claims.

    Args:
        token: The encoded JWT.
        expected_type: If provided, the token's ``type`` claim must match.

    Returns:
        The decoded claims dictionary.

    Raises:
        JWTError: If the signature is invalid, the token is expired, or the
            type does not match ``expected_type``.
    """
    claims = jwt.decode(token, _verifying_key(), algorithms=[ALGORITHM])
    if expected_type is not None and claims.get("type") != expected_type:
        raise JWTError(f"Expected token of type '{expected_type}'")
    return claims
