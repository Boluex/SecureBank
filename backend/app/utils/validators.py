"""Reusable input validation helpers.

Centralises the password-strength policy so it can be shared between the
Pydantic schemas and any other caller (for example the seed script).
"""

import re

MIN_PASSWORD_LENGTH = 10

_UPPERCASE_RE = re.compile(r"[A-Z]")
_LOWERCASE_RE = re.compile(r"[a-z]")
_DIGIT_RE = re.compile(r"[0-9]")
_SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength(password: str) -> str:
    """Validate that a password meets the minimum strength policy.

    The policy requires at least ``MIN_PASSWORD_LENGTH`` characters and a mix
    of uppercase, lowercase, numeric and special characters.

    Args:
        password: The candidate plaintext password.

    Returns:
        The original password, unchanged, when it is valid.

    Raises:
        ValueError: If the password fails any policy rule.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    if not _UPPERCASE_RE.search(password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not _LOWERCASE_RE.search(password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not _DIGIT_RE.search(password):
        raise ValueError("Password must contain at least one digit")
    if not _SPECIAL_RE.search(password):
        raise ValueError("Password must contain at least one special character")
    return password
