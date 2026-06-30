"""Bank account business logic.

Creates accounts with encrypted balances, enforces ownership on reads and
deletes, and exposes a helper that decrypts a stored balance for responses.
"""

import secrets
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_balance, encrypt_balance
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.schemas.account import AccountCreate, AccountPublic


def _generate_account_number() -> str:
    """Return a unique 16-digit account number as a string."""
    return "".join(secrets.choice("0123456789") for _ in range(16))


def to_public(account: Account) -> AccountPublic:
    """Build an :class:`AccountPublic` with the balance decrypted on the fly."""
    return AccountPublic(
        id=account.id,
        account_number=account.account_number,
        currency=account.currency,
        balance=decrypt_balance(account.encrypted_balance),
        created_at=account.created_at,
    )


def create_account(db_session: Session, user_id: int, payload: AccountCreate) -> Account:
    """Create a new account for a user, optionally seeding an initial deposit.

    The opening balance is encrypted before being stored, and a matching
    deposit transaction is recorded when ``initial_deposit`` is positive.
    """
    opening_balance = Decimal(payload.initial_deposit)
    account = Account(
        user_id=user_id,
        account_number=_generate_account_number(),
        encrypted_balance=encrypt_balance(opening_balance),
        currency=payload.currency,
    )
    db_session.add(account)
    db_session.flush()

    if opening_balance > 0:
        db_session.add(
            Transaction(
                account_id=account.id,
                type=TransactionType.DEPOSIT,
                amount=opening_balance,
                description="Opening deposit",
                reference_id=secrets.token_hex(18),
            )
        )

    db_session.commit()
    db_session.refresh(account)
    return account


def list_accounts(db_session: Session, user_id: int) -> list[Account]:
    """Return all accounts owned by the given user, newest first."""
    return (
        db_session.query(Account)
        .filter(Account.user_id == user_id)
        .order_by(Account.created_at.desc())
        .all()
    )


def get_owned_account(db_session: Session, account_id: int, user_id: int) -> Account:
    """Return an account by id, ensuring it belongs to the requesting user.

    Raises:
        HTTPException: 404 if the account does not exist or is owned by
            someone else (the same status is used to avoid leaking existence).
    """
    account = (
        db_session.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


def delete_account(db_session: Session, account_id: int, user_id: int) -> None:
    """Delete an owned account, refusing to close one with a non-zero balance.

    Raises:
        HTTPException: 404 if not found, 409 if the balance is not zero.
    """
    account = get_owned_account(db_session, account_id, user_id)
    if decrypt_balance(account.encrypted_balance) != Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot close an account with a non-zero balance",
        )
    db_session.delete(account)
    db_session.commit()
