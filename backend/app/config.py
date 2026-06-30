"""Application configuration loaded from environment variables.

All settings are sourced from the environment (or a local ``.env`` file)
using ``pydantic-settings``. No secret or credential is hardcoded here.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Attributes mirror the variables documented in ``.env.example``.
    """

    database_url: str
    secret_key: str

    private_key_path: str = "./keys/private.pem"
    public_key_path: str = "./keys/public.pem"
    encryption_key: str

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    max_transaction_amount: float = 1_000_000.0
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return the configured CORS origins as a clean list of strings."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    def read_private_key(self) -> str:
        """Read and return the PEM-encoded RSA private key used to sign JWTs."""
        return Path(self.private_key_path).read_text(encoding="utf-8")

    def read_public_key(self) -> str:
        """Read and return the PEM-encoded RSA public key used to verify JWTs."""
        return Path(self.public_key_path).read_text(encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton ``Settings`` instance.

    Caching avoids re-reading the environment on every request while keeping
    the settings object easy to override in tests.
    """
    return Settings()
