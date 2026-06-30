"""FastAPI application entry point for SecureBank.

Wires together middleware, rate limiting, CORS and the resource routers.
Database tables are created on startup for convenience in development.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limit import limiter
from app.database import Base, engine
from app.models import Account, RefreshToken, Transaction, User  # noqa: F401  (register tables)
from app.routes import accounts, auth, transactions

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecureBank API", version="1.0.0", debug=settings.debug)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Lightweight liveness probe used by orchestrators and tests."""
    return {"status": "ok"}
