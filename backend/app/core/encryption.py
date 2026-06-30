"""Symmetric encryption of sensitive data at rest using Fernet.

Account balances are encrypted with a Fernet key supplied via the
``ENCRYPTION_KEY`` environment variable. The plaintext balance only ever
exists in memory while a transaction is being processed.
"""

from decimal import Decimal
from functools import lru_cache

from cryptography.fernet import Fernet

from app.config import get_settings


@lru_cache
def _get_fernet() -> Fernet:
    """Return a cached Fernet instance built from the configured key."""
    settings = get_settings()
    return Fernet(settings.encryption_key.encode("utf-8"))


def encrypt_balance(balance: Decimal) -> str:
    """Encrypt a decimal balance into a Fernet ciphertext string.

    Args:
        balance: The plaintext account balance.

    Returns:
        A URL-safe ciphertext string suitable for database storage.
    """
    plaintext = format(balance.quantize(Decimal("0.01")), "f")
    token = _get_fernet().encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_balance(ciphertext: str) -> Decimal:
    """Decrypt a Fernet ciphertext back into a decimal balance.

    Args:
        ciphertext: The stored ciphertext produced by :func:`encrypt_balance`.

    Returns:
        The plaintext balance as a :class:`~decimal.Decimal`.
    """
    plaintext = _get_fernet().decrypt(ciphertext.encode("utf-8"))
    return Decimal(plaintext.decode("utf-8")).quantize(Decimal("0.01"))
