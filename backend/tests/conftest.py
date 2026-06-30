"""Shared pytest fixtures.

The environment is configured *before* any application module is imported so
that settings, the database engine and the RSA/Fernet keys all resolve to
test-only values. Each test runs against a fresh, file-backed SQLite database.
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

_TEST_DIR = Path(tempfile.mkdtemp(prefix="securebank_test_"))


def _write_rsa_keypair() -> tuple[Path, Path]:
    """Generate an RSA key pair on disk and return the (private, public) paths."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_path = _TEST_DIR / "private.pem"
    public_path = _TEST_DIR / "public.pem"
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return private_path, public_path


_private_path, _public_path = _write_rsa_keypair()
os.environ.update(
    DATABASE_URL=f"sqlite:///{_TEST_DIR / 'test.db'}",
    SECRET_KEY="test-secret-key-not-for-production",
    ENCRYPTION_KEY=Fernet.generate_key().decode("utf-8"),
    PRIVATE_KEY_PATH=str(_private_path),
    PUBLIC_KEY_PATH=str(_public_path),
    ACCESS_TOKEN_EXPIRE_MINUTES="15",
    REFRESH_TOKEN_EXPIRE_DAYS="7",
    ALLOWED_ORIGINS="http://localhost:3000",
    MAX_TRANSACTION_AMOUNT="1000000",
    DEBUG="true",
)

# Imported after the environment is primed so the engine binds to SQLite.
from fastapi.testclient import TestClient  # noqa: E402

from app.core.rate_limit import limiter  # noqa: E402
from app.database import Base, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402

# Rate limiting is a production safeguard, not behaviour under test. Disabling
# it keeps slowapi's per-address counters from bleeding across the many
# register/login calls the suite makes from a single TestClient address.
limiter.enabled = False


@pytest.fixture(autouse=True)
def _reset_database() -> Generator[None, None, None]:
    """Recreate all tables before each test for full isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a ``TestClient`` bound to the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Generator:
    """Yield a raw database session for tests that touch persistence directly."""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()


# Valid demo registration payload reused across the auth/account/txn tests.
VALID_USER = {
    "email": "test.user@example.com",
    "full_name": "Test User",
    "password": "Str0ng!Passw0rd",
}


@pytest.fixture
def registered_client(client: TestClient) -> TestClient:
    """Return a client that has registered and logged in ``VALID_USER``.

    The login response sets httpOnly auth cookies on the client's cookie jar,
    so subsequent requests are automatically authenticated.
    """
    client.post("/auth/register", json=VALID_USER)
    client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    return client
