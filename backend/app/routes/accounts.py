"""Bank account routes: create, list, retrieve and delete accounts."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.account import AccountCreate, AccountPublic
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountPublic, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> AccountPublic:
    """Open a new bank account for the authenticated user."""
    account = account_service.create_account(db_session, current_user.id, payload)
    return account_service.to_public(account)


@router.get("", response_model=list[AccountPublic])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> list[AccountPublic]:
    """List all accounts owned by the authenticated user."""
    accounts = account_service.list_accounts(db_session, current_user.id)
    return [account_service.to_public(account) for account in accounts]


@router.get("/{account_id}", response_model=AccountPublic)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> AccountPublic:
    """Retrieve a single account owned by the authenticated user."""
    account = account_service.get_owned_account(db_session, account_id, current_user.id)
    return account_service.to_public(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> None:
    """Close an account owned by the authenticated user (must be empty)."""
    account_service.delete_account(db_session, account_id, current_user.id)
