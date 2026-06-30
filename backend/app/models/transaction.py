"""Transaction ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransactionType:
    """Enumeration of the supported transaction types."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class Transaction(Base):
    """An immutable ledger entry recording a deposit or withdrawal.

    Transaction amounts are stored in plaintext (they are not, on their own,
    sensitive enough to encrypt) using a fixed-precision ``Numeric`` column to
    avoid floating point rounding errors.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    reference_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    account: Mapped["Account"] = relationship(  # noqa: F821
        "Account", back_populates="transactions"
    )
