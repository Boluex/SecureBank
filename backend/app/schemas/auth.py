"""Pydantic schemas for authentication and user resources."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.validators import validate_password_strength


class UserRegister(BaseModel):
    """Payload accepted by ``POST /auth/register``."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, value: str) -> str:
        """Enforce the shared password-strength policy."""
        return validate_password_strength(value)


class UserLogin(BaseModel):
    """Payload accepted by ``POST /auth/login``."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenRefreshRequest(BaseModel):
    """Optional body for ``POST /auth/refresh`` when not using cookies."""

    refresh_token: str | None = None


class TokenPair(BaseModel):
    """Access/refresh token pair returned by login and refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    """User representation safe to return to clients (no password hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
