"""Transaction business logic: deposits, withdrawals and history.

All monetary maths uses :class:`~decimal.Decimal`. Balances are decrypted,
adjusted and re-encrypted within a single database transaction so the stored
ciphertext always reflects a consistent state.
"""

import secrets
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.encryption import decrypt_balance, encrypt_balance
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate
from app.services.account_service import get_owned_account


def _enforce_transaction_limit(amount: Decimal) -> None:
    """Reject amounts above the configured per-transaction maximum.

    Raises:
        HTTPException: 422 if ``amount`` exceeds ``MAX_TRANSACTION_AMOUNT``.
    """
    maximum = Decimal(str(get_settings().max_transaction_amount))
    if amount > maximum:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Amount exceeds the maximum allowed transaction of {maximum}",
        )


def _record_transaction(
    db_session: Session, account: Account, transaction_type: str, payload: TransactionCreate
) -> Transaction:
    """Persist a transaction row for the given account."""
    transaction = Transaction(
        account_id=account.id,
        type=transaction_type,
        amount=Decimal(payload.amount),
        description=payload.description,
        reference_id=secrets.token_hex(18),
    )
    db_session.add(transaction)
    return transaction


def deposit(
    db_session: Session, account_id: int, user_id: int, payload: TransactionCreate
) -> Transaction:
    """Credit an owned account and record the deposit transaction."""
    amount = Decimal(payload.amount)
    _enforce_transaction_limit(amount)

    account = get_owned_account(db_session, account_id, user_id)
    new_balance = decrypt_balance(account.encrypted_balance) + amount
    account.encrypted_balance = encrypt_balance(new_balance)

    transaction = _record_transaction(db_session, account, TransactionType.DEPOSIT, payload)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


def withdraw(
    db_session: Session, account_id: int, user_id: int, payload: TransactionCreate
) -> Transaction:
    """Debit an owned account, rejecting overdrafts, and record the withdrawal.

    Raises:
        HTTPException: 422 over the limit, 400 on insufficient funds.
    """
    amount = Decimal(payload.amount)
    _enforce_transaction_limit(amount)

    account = get_owned_account(db_session, account_id, user_id)
    current_balance = decrypt_balance(account.encrypted_balance)
    if amount > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds"
        )

    account.encrypted_balance = encrypt_balance(current_balance - amount)
    transaction = _record_transaction(db_session, account, TransactionType.WITHDRAWAL, payload)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


def list_transactions(db_session: Session, account_id: int, user_id: int) -> list[Transaction]:
    """Return the transaction history of an owned account, newest first."""
    get_owned_account(db_session, account_id, user_id)
    return (
        db_session.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .all()
    )
