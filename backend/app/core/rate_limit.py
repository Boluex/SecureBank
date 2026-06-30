"""Shared rate limiter configuration built on slowapi.

A single ``Limiter`` instance is created here and imported by the routes and
the application factory so the limits are applied consistently.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed on the caller's remote address. Individual endpoints add their own
# stricter limits via the ``@limiter.limit(...)`` decorator.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# Limit applied specifically to authentication endpoints to slow down
# credential-stuffing and brute-force attempts.
AUTH_RATE_LIMIT = "10/minute"
