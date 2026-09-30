"""The security boundary: patient data must never be reachable unauthenticated.

Before the resume, GET /patients/ returned the entire patient table to anyone
who asked. These tests exist so that cannot regress.
"""

import pytest
from conftest import STAFF_PASSWORD, auth_header

PATIENT_ROUTES = [
    ("get", "/patients/"),
    ("post", "/patients/"),
    ("get", "/patients/1"),
    ("put", "/patients/1"),
    ("delete", "/patients/1"),
    ("get", "/appointments/"),
    ("post", "/appointments/"),
    ("get", "/bookings/"),
    ("get", "/users/"),
]


@pytest.mark.parametrize("method,path", PATIENT_ROUTES)
def test_phi_routes_reject_anonymous_callers(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code in (401, 405), (
        f"{method.upper()} {path} answered {response.status_code} without a token"
    )


def test_patient_list_is_not_public_even_when_patients_exist(client, session, patient):
    """The strongest form of the check: real rows exist, and still 401."""

    assert patient.id is not None

    response = client.get("/patients/")

    assert response.status_code == 401
    assert "meera" not in response.text.lower()


def test_malformed_token_is_rejected(client):
    response = client.get("/patients/", headers=auth_header("not-a-real-token"))

    assert response.status_code == 401


def test_token_signed_with_the_wrong_key_is_rejected(client):
    from jose import jwt

    # Correct claims, but signed with an attacker's key.
    forged = jwt.encode({"sub": "drarya"}, "attacker-key", algorithm="HS256")

    response = client.get("/patients/", headers=auth_header(forged))

    assert response.status_code == 401


def test_expired_token_is_rejected(client, staff):
    from datetime import timedelta

    from app.auth import create_access_token

    expired = create_access_token(
        {"sub": "drarya"}, expires_delta=timedelta(minutes=-5)
    )

    response = client.get("/patients/", headers=auth_header(expired))

    assert response.status_code == 401


def test_staff_can_read_patients(client, staff_token, patient):
    response = client.get("/patients/", headers=auth_header(staff_token))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == "meera.rao@example.com"


def test_wrong_password_is_rejected(client, staff):
    response = client.post(
        "/token", data={"username": "drarya", "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_unknown_user_gives_the_same_message_as_a_bad_password(client, staff):
    unknown = client.post(
        "/token", data={"username": "nobody", "password": STAFF_PASSWORD}
    )
    wrong = client.post(
        "/token", data={"username": "drarya", "password": "wrong-password"}
    )

    # Identical responses, so the endpoint cannot be used to enumerate accounts.
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()


def test_inactive_user_cannot_log_in(client, session, staff):
    staff.is_active = False
    session.commit()

    response = client.post(
        "/token", data={"username": "drarya", "password": STAFF_PASSWORD}
    )

    assert response.status_code == 401


def test_only_admin_can_create_users(client, staff_token):
    response = client.post(
        "/users/",
        headers=auth_header(staff_token),
        json={
            "username": "newstaff",
            "email": "new@nymalay.clinic",
            "password": "some-long-password",
        },
    )

    assert response.status_code == 403


def test_admin_can_create_users(client, admin_token):
    response = client.post(
        "/users/",
        headers=auth_header(admin_token),
        json={
            "username": "newstaff",
            "email": "new@nymalay.clinic",
            "password": "some-long-password",
        },
    )

    assert response.status_code == 201
    assert "password" not in response.json()


def test_user_response_never_leaks_the_password_hash(client, staff_token):
    response = client.get("/users/me", headers=auth_header(staff_token))

    assert response.status_code == 200
    body = response.text.lower()
    assert "hashed_password" not in body
    assert "$2b$" not in body
