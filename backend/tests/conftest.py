"""Shared pytest fixtures.

Every test runs against a throwaway SQLite file created per session, so the
suite never touches the developer's clinic.db and can run in any order.
"""

import os
import tempfile
from datetime import date, datetime, timedelta, timezone

import pytest

# Point the app at a temp database *before* app modules read their settings.
_TMP_DIR = tempfile.mkdtemp(prefix="nymalay-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
os.environ["SECRET_KEY"] = "test-secret-key-not-used-in-production-0123456789"
os.environ["ENVIRONMENT"] = "test"
os.environ["ADMIN_PASSWORD"] = ""  # never auto-seed during tests
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

# The booking and appointment routes are gated off by default, because the public
# site books nothing. The existing suite exercises their CRUD and scheduling
# logic, so it opens the gate here. `test_public_booking_api_gate.py` covers the
# closed state, which is the one the deployed site actually runs in.
os.environ["ENABLE_LEGACY_BOOKING_API"] = "true"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import crud, schemas  # noqa: E402
from app.auth import get_password_hash  # noqa: E402
from app.database import Base, enable_sqlite_foreign_keys, get_db  # noqa: E402
from app.main import app  # noqa: E402

STAFF_PASSWORD = "correct-horse-battery"
ADMIN_PASSWORD = "admin-passphrase-1"


@pytest.fixture()
def engine():
    # StaticPool + in-memory keeps every connection pointed at the same database.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Same pragma the app applies, so ON DELETE CASCADE behaves in tests
    # exactly as it does in production SQLite.
    enable_sqlite_foreign_keys(engine)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def session(engine):
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def staff(session):
    return crud.create_user(
        session,
        schemas.UserCreate(
            username="drarya",
            email="arya@nymalay.clinic",
            full_name="Dr. Arya",
            password=STAFF_PASSWORD,
        ),
        get_password_hash(STAFF_PASSWORD),
    )


@pytest.fixture()
def admin(session):
    return crud.create_user(
        session,
        schemas.UserCreate(
            username="admin",
            email="admin@nymalay.clinic",
            password=ADMIN_PASSWORD,
            is_admin=True,
        ),
        get_password_hash(ADMIN_PASSWORD),
    )


@pytest.fixture()
def patient(session):
    return crud.create_patient(
        session,
        schemas.PatientCreate(
            first_name="Meera",
            last_name="Rao",
            email="meera.rao@example.com",
            phone="+919876543210",
            date_of_birth=date(1990, 4, 12),
        ),
    )


def login(client, username, password) -> str:
    """Return a bearer token for the given staff account."""

    response = client.post(
        "/token", data={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def staff_token(client, staff):
    return login(client, "drarya", STAFF_PASSWORD)


@pytest.fixture()
def admin_token(client, admin):
    return login(client, "admin", ADMIN_PASSWORD)


@pytest.fixture()
def future_date():
    return date.today() + timedelta(days=7)


@pytest.fixture()
def future_datetime():
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
