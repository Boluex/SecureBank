"""Database engine, session factory and declarative base.

Provides a SQLAlchemy engine configured from ``DATABASE_URL`` and a
``get_db`` dependency that yields a scoped session per request.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# SQLite (used by the test-suite) needs a couple of extra connect args so the
# in-process engine can be shared across the TestClient's worker thread.
_engine_kwargs: dict = {"pool_pre_ping": True, "future": True}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

# ``pool_pre_ping`` transparently recycles stale connections, which is
# important for long-lived deployments behind a connection pooler.
engine = create_engine(settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and guarantee it is closed afterwards.

    Used as a FastAPI dependency so each request operates on its own
    transactional session.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
