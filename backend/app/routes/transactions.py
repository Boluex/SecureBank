"""Transaction routes: deposit, withdraw and transaction history."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionPublic
from app.services import transaction_service

router = APIRouter(prefix="/accounts", tags=["transactions"])


@router.post(
    "/{account_id}/deposit",
    response_model=TransactionPublic,
    status_code=status.HTTP_201_CREATED,
)
def deposit(
    account_id: int,
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> TransactionPublic:
    """Deposit money into an account owned by the authenticated user."""
    transaction = transaction_service.deposit(db_session, account_id, current_user.id, payload)
    return TransactionPublic.model_validate(transaction)


@router.post(
    "/{account_id}/withdraw",
    response_model=TransactionPublic,
    status_code=status.HTTP_201_CREATED,
)
def withdraw(
    account_id: int,
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> TransactionPublic:
    """Withdraw money from an account owned by the authenticated user."""
    transaction = transaction_service.withdraw(db_session, account_id, current_user.id, payload)
    return TransactionPublic.model_validate(transaction)


@router.get("/{account_id}/transactions", response_model=list[TransactionPublic])
def list_transactions(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> list[TransactionPublic]:
    """Return the transaction history for an owned account."""
    transactions = transaction_service.list_transactions(db_session, account_id, current_user.id)
    return [TransactionPublic.model_validate(item) for item in transactions]
