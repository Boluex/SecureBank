"""FastAPI dependencies for authentication and authorization.

The current user is resolved from a bearer access token, accepted either via
the ``Authorization`` header or an ``access_token`` httpOnly cookie (used by
the React frontend).
"""

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.database import get_db
from app.models.user import User

ACCESS_COOKIE_NAME = "access_token"

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _extract_access_token(request: Request) -> str:
    """Return the access token from the Authorization header or cookie.

    Raises:
        HTTPException: 401 if no token is present in either location.
    """
    authorization = request.headers.get("Authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()

    cookie_token = request.cookies.get(ACCESS_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    raise _credentials_error


def get_current_user(request: Request, db_session: Session = Depends(get_db)) -> User:
    """Resolve and return the authenticated, active user for the request.

    Raises:
        HTTPException: 401 if the token is missing/invalid, 403 if the user
            account has been deactivated.
    """
    token = _extract_access_token(request)
    try:
        claims = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    except JWTError as error:
        raise _credentials_error from error

    user_id = claims.get("sub")
    if user_id is None:
        raise _credentials_error

    user = db_session.get(User, int(user_id))
    if user is None:
        raise _credentials_error
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )
    return user
