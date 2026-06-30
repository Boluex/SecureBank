"""Pydantic schemas for bank account resources."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """Payload accepted by ``POST /accounts``.

    A new account starts at a zero balance unless a non-negative
    ``initial_deposit`` is supplied.
    """

    currency: str = Field(default="USD", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    initial_deposit: Decimal = Field(default=Decimal("0"), ge=0, max_digits=18, decimal_places=2)


class AccountPublic(BaseModel):
    """Account representation returned to clients with a decrypted balance."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    account_number: str
    currency: str
    balance: Decimal
    created_at: datetime
