"""Tests for the deposit, withdraw and transaction history endpoints."""

from fastapi.testclient import TestClient


def _open_account(client: TestClient, initial_deposit: str = "0") -> int:
    """Helper that opens an account and returns its id."""
    response = client.post("/accounts", json={"initial_deposit": initial_deposit})
    return response.json()["id"]


def test_deposit_increases_balance(registered_client: TestClient) -> None:
    """A deposit credits the account and records a transaction."""
    account_id = _open_account(registered_client)
    response = registered_client.post(
        f"/accounts/{account_id}/deposit", json={"amount": "150.50", "description": "Paycheck"}
    )
    assert response.status_code == 201
    assert response.json()["type"] == "deposit"

    balance = registered_client.get(f"/accounts/{account_id}").json()["balance"]
    assert balance == "150.50"


def test_withdraw_decreases_balance(registered_client: TestClient) -> None:
    """A withdrawal debits the account when funds are sufficient."""
    account_id = _open_account(registered_client, "200.00")
    response = registered_client.post(
        f"/accounts/{account_id}/withdraw", json={"amount": "75.00"}
    )
    assert response.status_code == 201

    balance = registered_client.get(f"/accounts/{account_id}").json()["balance"]
    assert balance == "125.00"


def test_withdraw_insufficient_funds(registered_client: TestClient) -> None:
    """Withdrawing more than the balance is rejected with 400."""
    account_id = _open_account(registered_client, "50.00")
    response = registered_client.post(
        f"/accounts/{account_id}/withdraw", json={"amount": "100.00"}
    )
    assert response.status_code == 400


def test_negative_amount_rejected(registered_client: TestClient) -> None:
    """A non-positive deposit amount fails schema validation with 422."""
    account_id = _open_account(registered_client)
    response = registered_client.post(
        f"/accounts/{account_id}/deposit", json={"amount": "-10.00"}
    )
    assert response.status_code == 422


def test_over_limit_amount_rejected(registered_client: TestClient) -> None:
    """A deposit above the configured maximum is rejected with 422."""
    account_id = _open_account(registered_client)
    response = registered_client.post(
        f"/accounts/{account_id}/deposit", json={"amount": "9999999.00"}
    )
    assert response.status_code == 422


def test_transaction_history(registered_client: TestClient) -> None:
    """The history endpoint returns all transactions for the account."""
    account_id = _open_account(registered_client, "100.00")
    registered_client.post(f"/accounts/{account_id}/deposit", json={"amount": "25.00"})
    registered_client.post(f"/accounts/{account_id}/withdraw", json={"amount": "10.00"})

    response = registered_client.get(f"/accounts/{account_id}/transactions")
    assert response.status_code == 200
    history = response.json()
    # Opening deposit + deposit + withdrawal == 3 entries.
    assert len(history) == 3
    assert {item["type"] for item in history} == {"deposit", "withdrawal"}
