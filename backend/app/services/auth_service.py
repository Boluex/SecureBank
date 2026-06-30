"""Authentication business logic.

Handles user registration, credential verification and the full lifecycle of
refresh tokens (issue, rotate, revoke) used for JWT authentication.
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from jose import JWTError

from app.config import get_settings
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import UserRegister


def _as_utc(moment: datetime) -> datetime:
    """Return a timezone-aware UTC datetime.

    Postgres preserves the timezone on ``DateTime(timezone=True)`` columns, but
    some backends (notably SQLite, used by the test-suite) return naive values.
    Treating a naive timestamp as UTC keeps expiry comparisons safe everywhere.
    """
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment


def register_user(db_session: Session, payload: UserRegister) -> User:
    """Create a new user, rejecting duplicate email addresses.

    Raises:
        HTTPException: 409 if the email is already registered.
    """
    existing_user = db_session.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered"
        )

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user


def authenticate_user(db_session: Session, email: str, password: str) -> User:
    """Verify credentials and return the matching active user.

    Raises:
        HTTPException: 401 for unknown email/wrong password, 403 if inactive.
    """
    user = db_session.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )
    return user


def _store_refresh_token(db_session: Session, user_id: int, refresh_token: str) -> None:
    """Persist the SHA-256 hash of a freshly issued refresh token."""
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    record = RefreshToken(
        user_id=user_id, token_hash=hash_token(refresh_token), expires_at=expires_at, revoked=False
    )
    db_session.add(record)
    db_session.commit()


def issue_token_pair(db_session: Session, user: User) -> tuple[str, str]:
    """Issue a new access/refresh token pair and persist the refresh token."""
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    _store_refresh_token(db_session, user.id, refresh_token)
    return access_token, refresh_token


def _get_active_token_record(db_session: Session, refresh_token: str) -> RefreshToken:
    """Return the stored, non-revoked, unexpired record for a refresh token.

    Raises:
        HTTPException: 401 if the token is unknown, revoked or expired.
    """
    record = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token(refresh_token))
        .first()
    )
    if record is None or record.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or revoked"
        )
    if _as_utc(record.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )
    return record


def user_from_refresh_token(db_session: Session, refresh_token: str) -> User:
    """Decode a refresh token and return its active owning user.

    Validates both the JWT signature/type and the persisted token record.

    Raises:
        HTTPException: 401 if the token is malformed/invalid, 403 if inactive.
    """
    try:
        claims = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid"
        ) from error

    _get_active_token_record(db_session, refresh_token)
    user = db_session.get(User, int(claims["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )
    return user


def rotate_refresh_token(db_session: Session, user: User, refresh_token: str) -> tuple[str, str]:
    """Revoke the presented refresh token and issue a brand new pair.

    Rotating on every refresh limits the damage of a leaked refresh token.
    """
    record = _get_active_token_record(db_session, refresh_token)
    record.revoked = True
    db_session.commit()
    return issue_token_pair(db_session, user)


def revoke_refresh_token(db_session: Session, refresh_token: str) -> None:
    """Blacklist a refresh token on logout (idempotent)."""
    record = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token(refresh_token))
        .first()
    )
    if record is not None and not record.revoked:
        record.revoked = True
        db_session.commit()
