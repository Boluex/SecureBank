"""Seed the database with deterministic demo data.

Creates three test users (whose credentials are printed to the console), two
accounts per user and ten random transactions per account. Run with::

    python -m app.utils.seed

The script is idempotent: it clears existing demo rows before reseeding.
"""

import random
import secrets
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_balance, encrypt_balance
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.user import User

# Known, non-production credentials used purely for local demos.
DEMO_PASSWORD = "Demo!Pass123"
DEMO_USERS = [
    {"email": "alice@example.com", "full_name": "Alice Johnson"},
    {"email": "bob@example.com", "full_name": "Bob Smith"},
    {"email": "carol@example.com", "full_name": "Carol Williams"},
]


def _reset_tables() -> None:
    """Drop and recreate all tables to guarantee a clean slate."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _create_account(db_session: Session, user: User) -> Account:
    """Create a single account with a random opening balance for a user."""
    opening_balance = Decimal(random.randint(500, 5000))
    account = Account(
        user_id=user.id,
        account_number="".join(secrets.choice("0123456789") for _ in range(16)),
        encrypted_balance=encrypt_balance(opening_balance),
        currency="USD",
    )
    db_session.add(account)
    db_session.flush()
    return account


def _seed_transactions(db_session: Session, account: Account, count: int = 10) -> None:
    """Generate ``count`` random deposits/withdrawals for an account."""
    balance = decrypt_balance(account.encrypted_balance)
    for index in range(count):
        is_deposit = random.choice([True, True, False])
        amount = Decimal(random.randint(10, 500))
        if not is_deposit and amount > balance:
            is_deposit = True
        transaction_type = TransactionType.DEPOSIT if is_deposit else TransactionType.WITHDRAWAL
        balance = balance + amount if is_deposit else balance - amount
        db_session.add(
            Transaction(
                account_id=account.id,
                type=transaction_type,
                amount=amount,
                description=f"Seed transaction #{index + 1}",
                reference_id=secrets.token_hex(18),
            )
        )
    account.encrypted_balance = encrypt_balance(balance)


def seed_database() -> None:
    """Populate the database with demo users, accounts and transactions."""
    _reset_tables()
    db_session = SessionLocal()
    try:
        for user_spec in DEMO_USERS:
            user = User(
                email=user_spec["email"],
                full_name=user_spec["full_name"],
                hashed_password=hash_password(DEMO_PASSWORD),
                is_active=True,
            )
            db_session.add(user)
            db_session.flush()
            for _ in range(2):
                account = _create_account(db_session, user)
                _seed_transactions(db_session, account)
        db_session.commit()
        _print_credentials()
    finally:
        db_session.close()


def _print_credentials() -> None:
    """Print the demo login credentials to the console."""
    print("\n" + "=" * 60)
    print("SecureBank demo data created. Login credentials:")
    print("=" * 60)
    for user_spec in DEMO_USERS:
        print(f"  email: {user_spec['email']:<28} password: {DEMO_PASSWORD}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    seed_database()
