"""Authentication routes: register, login, refresh and logout.

Tokens are returned in the JSON body (for API clients) and also set as
httpOnly cookies (for the React frontend). Auth endpoints are rate limited to
mitigate brute-force attacks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.dependencies import ACCESS_COOKIE_NAME
from app.core.rate_limit import AUTH_RATE_LIMIT, limiter
from app.database import get_db
from app.core.metrics import user_logins_total, user_registrations_total
from app.schemas.auth import TokenPair, TokenRefreshRequest, UserLogin, UserPublic, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Attach access and refresh tokens as httpOnly cookies to the response."""
    settings = get_settings()
    response.set_cookie(
        ACCESS_COOKIE_NAME, access_token, httponly=True, samesite="lax",
        secure=not settings.debug, max_age=settings.access_token_expire_minutes * 60, path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME, refresh_token, httponly=True, samesite="lax",
        secure=not settings.debug, max_age=settings.refresh_token_expire_days * 86400, path="/",
    )


def _read_refresh_token(request: Request, body: TokenRefreshRequest | None) -> str:
    """Return the refresh token from the request body or the cookie."""
    if body is not None and body.refresh_token:
        return body.refresh_token
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if cookie_token:
        return cookie_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not provided"
    )


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_RATE_LIMIT)
def register(
    request: Request, payload: UserRegister, db_session: Session = Depends(get_db)
) -> UserPublic:
    """Register a new user account."""
    try:
        user = auth_service.register_user(db_session, payload)
        user_registrations_total.labels(status="success").inc()
        return UserPublic.model_validate(user)
    except Exception as e:
        user_registrations_total.labels(status="failed").inc()
        raise e


@router.post("/login", response_model=TokenPair)
@limiter.limit(AUTH_RATE_LIMIT)
def login(
    request: Request, response: Response, payload: UserLogin,
    db_session: Session = Depends(get_db),
) -> TokenPair:
    """Authenticate a user and issue an access/refresh token pair."""
    try:
        user = auth_service.authenticate_user(db_session, payload.email, payload.password)
        access_token, refresh_token = auth_service.issue_token_pair(db_session, user)
        _set_auth_cookies(response, access_token, refresh_token)
        user_logins_total.labels(status="success").inc()
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        user_logins_total.labels(status="failed").inc()
        raise e


@router.post("/refresh", response_model=TokenPair)
@limiter.limit(AUTH_RATE_LIMIT)
def refresh(
    request: Request, response: Response,
    body: TokenRefreshRequest | None = None, db_session: Session = Depends(get_db),
) -> TokenPair:
    """Rotate a valid refresh token into a new access/refresh token pair."""
    refresh_token = _read_refresh_token(request, body)
    user = auth_service.user_from_refresh_token(db_session, refresh_token)
    access_token, new_refresh = auth_service.rotate_refresh_token(db_session, user, refresh_token)
    _set_auth_cookies(response, access_token, new_refresh)
    return TokenPair(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request, response: Response,
    body: TokenRefreshRequest | None = None, db_session: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoke the refresh token (blacklist) and clear the auth cookies."""
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    token = (body.refresh_token if body and body.refresh_token else cookie_token)
    if token:
        auth_service.revoke_refresh_token(db_session, token)
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return {"detail": "Successfully logged out"}
