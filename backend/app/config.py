"""Application settings, read once from the environment.

The previous code hardcoded the JWT secret in auth.py and read the database URL
inline in database.py, which meant the Docker Compose Postgres path could never
be configured without editing source. Everything tunable lives here now.
"""

import os
import secrets
import warnings
from functools import lru_cache

from dotenv import load_dotenv

# Load the backend's own .env regardless of the process working directory, so
# `uvicorn app.main:app` behaves the same from backend/ and from the repo root.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"

# The signing key that used to be hardcoded in auth.py. It is in git history,
# so it must never be trusted, even if somebody exports it explicitly.
# Listed here purely so an existing deployment carrying it fails at boot.
LEAKED_SECRET_KEY = (
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)

INSECURE_DEFAULTS = {
    "change-in-production",
    "your-secret-key-here-change-in-production",
    "secret",
    "changeme",
    "replace-me-with-openssl-rand-hex-32",
    LEAKED_SECRET_KEY,
}


class Settings:
    """Plain settings object. No dependency-injection framework needed for this."""

    def __init__(self) -> None:
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"

        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinic.db")

        # No usable default. The original hardcoded key was committed to the
        # repository, so anyone with the source could mint valid staff tokens.
        # Outside production we fall back to a random per-process key: it makes
        # local setup frictionless while invalidating every token on restart,
        # which is the safe failure mode for a throwaway key.
        configured_secret = os.getenv("SECRET_KEY", "").strip()
        if configured_secret and configured_secret not in INSECURE_DEFAULTS:
            self.SECRET_KEY = configured_secret
        else:
            self.SECRET_KEY = secrets.token_hex(32)
            if configured_secret:
                message = (
                    f"SECRET_KEY is set to a known placeholder value "
                    f"({configured_secret[:12]}...); ignoring it. "
                    "Generate a real one with: openssl rand -hex 32"
                )
            else:
                message = (
                    "SECRET_KEY is not set. Using a random key for this process "
                    "only, so tokens will not survive a restart. Set SECRET_KEY "
                    "for anything persistent."
                )
            if self.ENVIRONMENT.lower() in {"production", "prod"}:
                raise RuntimeError(
                    f"{message} Refusing to start with ENVIRONMENT="
                    f"{self.ENVIRONMENT}."
                )
            warnings.warn(message, RuntimeWarning, stacklevel=2)

        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        self.CORS_ORIGINS = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", DEFAULT_ORIGINS).split(",")
            if origin.strip()
        ]

        # Seeded admin account, used only by the seed script.
        self.ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        self.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@nymalay.clinic")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

        # The public site no longer books anything: the doctor reviews each
        # request, assigns the slot and confirms personally. The booking and
        # appointment routes stay in the codebase for a future direct-booking
        # phase, but are switched off by default so a stale tab, a bookmark or
        # a hand-typed URL cannot create a booking or accept a payment.
        # Opt back in explicitly with ENABLE_LEGACY_BOOKING_API=true.
        self.ENABLE_LEGACY_BOOKING_API = (
            os.getenv("ENABLE_LEGACY_BOOKING_API", "false").lower()
            in {"1", "true", "yes", "on"}
        )

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}

    def validate(self) -> None:
        """Fail loudly at boot rather than serving PHI with a guessable key."""
        if not self.is_production:
            return

        if (
            self.SECRET_KEY in INSECURE_DEFAULTS
            or self.SECRET_KEY == LEAKED_SECRET_KEY
            or len(self.SECRET_KEY) < 32
        ):
            raise RuntimeError(
                "SECRET_KEY must be set to a strong, unique value of at least 32 "
                "characters in production. Generate one with: openssl rand -hex 32"
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings


settings = get_settings()
