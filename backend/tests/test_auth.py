"""Tests for the authentication endpoints."""

from fastapi.testclient import TestClient

from tests.conftest import VALID_USER


def test_register_success(client: TestClient) -> None:
    """A valid registration returns 201 and the public user representation."""
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_USER["email"]
    assert "hashed_password" not in body


def test_register_duplicate_email(client: TestClient) -> None:
    """Registering the same email twice is rejected with 409."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post("/auth/register", json=VALID_USER)
    assert response.status_code == 409


def test_register_weak_password(client: TestClient) -> None:
    """A password that fails the strength policy is rejected with 422."""
    payload = {**VALID_USER, "password": "weak"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient) -> None:
    """Valid credentials return a token pair and set auth cookies."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] and body["refresh_token"]
    assert "access_token" in response.cookies


def test_login_wrong_password(client: TestClient) -> None:
    """An incorrect password is rejected with 401."""
    client.post("/auth/register", json=VALID_USER)
    response = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": "Wr0ng!Passw0rd"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client: TestClient, db_session) -> None:
    """A deactivated account cannot log in (403)."""
    from app.models.user import User

    client.post("/auth/register", json=VALID_USER)
    user = db_session.query(User).filter(User.email == VALID_USER["email"]).first()
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    assert response.status_code == 403


def test_refresh_rotates_tokens(client: TestClient) -> None:
    """Refreshing issues a new token pair and revokes the old refresh token."""
    client.post("/auth/register", json=VALID_USER)
    login = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    old_refresh = login.json()["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    # The rotated-out token must no longer be accepted.
    reused = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert reused.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    """After logout the refresh token is blacklisted and rejected."""
    client.post("/auth/register", json=VALID_USER)
    login = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 200

    reused = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reused.status_code == 401
