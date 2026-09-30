"""Password hashing, JWT issuing and the staff authentication guard.

The original file hardcoded the signing secret in source control, carried a
second `CryptContext` duplicating crud.py's, and had an `authenticate_user`
stub that always returned None. All three are gone: the secret now comes from
the environment, there is one hashing path, and authentication is a real
FastAPI dependency.

Hashing note: this used to go through passlib 1.7.4, which is unmaintained and
incompatible with bcrypt >= 4.1 - it crashes with "password cannot be longer
than 72 bytes" instead of truncating. That turned any user with a long password
into a 500 on the create-user route. We now call bcrypt directly and truncate
explicitly, so the limit is a documented behaviour rather than a crash.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud
from .config import settings
from .database import get_db

# bcrypt ignores anything past 72 bytes of the password.
BCRYPT_MAX_BYTES = 72

# A real hash of a throwaway value, used to spend the same time on a login for
# an account that does not exist as on one where the password is simply wrong.
_DUMMY_HASH = bcrypt.hashpw(b"nymalay-timing-equalizer", bcrypt.gensalt()).decode()

# tokenUrl must match the real route path or the Swagger "Authorize" button 401s.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def _to_bcrypt_bytes(password: str) -> bytes:
    raw = password.encode("utf-8")
    if len(raw) <= BCRYPT_MAX_BYTES:
        return raw
    return raw[:BCRYPT_MAX_BYTES]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            _to_bcrypt_bytes(plain_password), hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        # Malformed hash in the database; treat as a failed login, never a 500.
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        _to_bcrypt_bytes(password), bcrypt.gensalt()
    ).decode("utf-8")


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        # Hash anyway so a missing user and a wrong password take the same time
        # and cannot be distinguished by response latency.
        bcrypt.checkpw(b"x", _DUMMY_HASH.encode("utf-8"))
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    # utcnow() is deprecated in Python 3.12; fromutc keeps the JWT exp claim
    # timezone-aware as the spec requires.
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Return the claims, or None if the token is invalid or expired."""

    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None


CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_staff(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Dependency guarding every route that touches patient or booking data."""

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_access_token(token)
    if claims is None:
        raise CREDENTIALS_ERROR

    username = claims.get("sub")
    if not username:
        raise CREDENTIALS_ERROR

    user = crud.get_user_by_username(db, username)
    if user is None or not user.is_active:
        raise CREDENTIALS_ERROR

    return user


def require_admin(user=Depends(get_current_staff)):
    """Dependency for staff-management routes."""

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required",
        )
    return user
