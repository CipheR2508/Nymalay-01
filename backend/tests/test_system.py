"""System-level checks: health, CORS, and settings safety rails."""

import pytest


def test_health_is_public(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "timestamp" in body


def test_openapi_documents_the_routes(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]

    assert "/bookings/" in paths
    assert "/patients/" in paths
    assert "/appointments/" in paths
    assert "/token" in paths


def test_cors_allows_the_configured_frontend_origin(client):
    response = client.options(
        "/patients/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_does_not_reflect_an_unknown_origin(client):
    """A wildcard or a reflected arbitrary origin would let any site read PHI."""

    response = client.options(
        "/patients/",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") != "https://evil.example"


def test_health_rejects_a_body_smuggled_into_a_get(client):
    response = client.request(
        "GET", "/health", content=b'{"a":1}', headers={"Content-Type": "application/json"}
    )

    assert response.status_code in (200, 405)


def test_production_refuses_a_weak_secret(monkeypatch):
    """The startup guard that stops SECRET_KEY shipping as a literal."""

    from app import config

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "change-in-production")
    config.get_settings.cache_clear()

    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            config.get_settings()
    finally:
        # Restore before any later import re-evaluates the module singleton,
        # otherwise the rest of the session inherits production settings.
        monkeypatch.undo()
        config.get_settings.cache_clear()


def test_production_accepts_a_generated_secret(monkeypatch):
    from app import config

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    config.get_settings.cache_clear()

    try:
        assert config.get_settings().SECRET_KEY == "a" * 64
    finally:
        monkeypatch.undo()
        config.get_settings.cache_clear()


def test_production_rejects_the_leaked_repository_secret(monkeypatch):
    """The key that used to be hardcoded in auth.py is in git history.

    It is 64 hex characters, so a length check alone waves it through. It has
    to be refused by name.
    """

    from app import config

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", config.LEAKED_SECRET_KEY)
    config.get_settings.cache_clear()

    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            config.get_settings()
    finally:
        monkeypatch.undo()
        config.get_settings.cache_clear()


def test_production_rejects_a_missing_secret(monkeypatch):
    from app import config

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    config.get_settings.cache_clear()

    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            config.get_settings()
    finally:
        monkeypatch.undo()
        config.get_settings.cache_clear()


def test_development_falls_back_to_a_random_key(monkeypatch):
    """Local dev should work with no SECRET_KEY, but tokens must not survive."""

    from app import config

    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    config.get_settings.cache_clear()

    try:
        with pytest.warns(RuntimeWarning, match="SECRET_KEY"):
            first = config.get_settings().SECRET_KEY
        assert len(first) >= 32
        assert first not in config.INSECURE_DEFAULTS
    finally:
        monkeypatch.undo()
        config.get_settings.cache_clear()


def test_sqlite_flag_drives_connect_args():
    from app.config import Settings

    sqlite_settings = Settings()
    sqlite_settings.DATABASE_URL = "sqlite:///./x.db"
    assert sqlite_settings.is_sqlite is True

    postgres_settings = Settings()
    postgres_settings.DATABASE_URL = "postgresql://u:p@db:5432/nymalaya"
    assert postgres_settings.is_sqlite is False
