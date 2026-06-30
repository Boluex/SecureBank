"""Pydantic schemas for transaction resources."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    """Payload accepted by the deposit and withdraw endpoints.

    The amount must be strictly positive; the upper bound is additionally
    enforced in the service layer against ``MAX_TRANSACTION_AMOUNT``.
    """

    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    description: str = Field(default="", max_length=255)


class TransactionPublic(BaseModel):
    """Transaction representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: str
    amount: Decimal
    description: str
    reference_id: str
    created_at: datetime
