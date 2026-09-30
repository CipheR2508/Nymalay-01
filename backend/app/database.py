"""Database engine and session factory."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base.

    Replaces `declarative_base()` from `sqlalchemy.ext.declarative`, which has
    been deprecated since SQLAlchemy 2.0.
    """


def enable_sqlite_foreign_keys(target: Engine) -> None:
    """Make SQLite honour ON DELETE CASCADE.

    SQLite parses foreign key clauses but ignores them unless enforcement is
    switched on per connection. Without this, deleting a patient leaves their
    appointments behind in local dev, while the same code cascades correctly
    against PostgreSQL. That divergence is how orphaned rows appear only on
    developer machines.
    """

    @event.listens_for(target, "connect")
    def _set_pragma(dbapi_connection, _record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# `check_same_thread` is a SQLite-only keyword. Passing it to a PostgreSQL
# engine raised TypeError, so the Docker Compose setup in docker-compose.yml
# could never actually boot. Pick the kwargs per backend instead.
if settings.is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    enable_sqlite_foreign_keys(engine)
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency yielding a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
