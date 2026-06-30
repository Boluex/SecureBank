"""Tests for the bank account endpoints."""

from fastapi.testclient import TestClient


def test_create_account(registered_client: TestClient) -> None:
    """A logged-in user can open an account with an initial deposit."""
    response = registered_client.post("/accounts", json={"initial_deposit": "100.00"})
    assert response.status_code == 201
    body = response.json()
    assert body["balance"] == "100.00"
    assert len(body["account_number"]) == 16


def test_create_account_requires_auth(client: TestClient) -> None:
    """Account creation without authentication is rejected with 401."""
    response = client.post("/accounts", json={"initial_deposit": "0"})
    assert response.status_code == 401


def test_list_accounts(registered_client: TestClient) -> None:
    """Listing returns exactly the accounts owned by the user."""
    registered_client.post("/accounts", json={"initial_deposit": "10.00"})
    registered_client.post("/accounts", json={"initial_deposit": "20.00"})
    response = registered_client.get("/accounts")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_account_by_id(registered_client: TestClient) -> None:
    """A user can retrieve a specific account they own."""
    created = registered_client.post("/accounts", json={"initial_deposit": "55.00"})
    account_id = created.json()["id"]
    response = registered_client.get(f"/accounts/{account_id}")
    assert response.status_code == 200
    assert response.json()["id"] == account_id


def test_get_missing_account_returns_404(registered_client: TestClient) -> None:
    """Requesting a non-existent account returns 404."""
    response = registered_client.get("/accounts/999999")
    assert response.status_code == 404


def test_delete_empty_account(registered_client: TestClient) -> None:
    """An account with a zero balance can be closed."""
    created = registered_client.post("/accounts", json={"initial_deposit": "0"})
    account_id = created.json()["id"]
    response = registered_client.delete(f"/accounts/{account_id}")
    assert response.status_code == 204
    assert registered_client.get(f"/accounts/{account_id}").status_code == 404


def test_delete_account_with_balance_blocked(registered_client: TestClient) -> None:
    """Closing an account that still holds money is refused with 409."""
    created = registered_client.post("/accounts", json={"initial_deposit": "75.00"})
    account_id = created.json()["id"]
    response = registered_client.delete(f"/accounts/{account_id}")
    assert response.status_code == 409
