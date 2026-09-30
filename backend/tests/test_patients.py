"""Patient and appointment CRUD, plus the referential integrity the old schema
was missing (appointments.patient_id was a bare integer, not a foreign key).
"""

import pytest
from conftest import auth_header


def patient_payload(**overrides):
    from datetime import date

    payload = {
        "first_name": "Meera",
        "last_name": "Rao",
        "email": "meera.rao@example.com",
        "phone": "+919876543210",
        "date_of_birth": "1990-04-12",
    }
    payload.update(overrides)
    return payload


def test_create_patient(client, staff_token):
    response = client.post(
        "/patients/", headers=auth_header(staff_token), json=patient_payload()
    )

    assert response.status_code == 201, response.text
    assert response.json()["email"] == "meera.rao@example.com"
    assert response.json()["date_of_birth"] == "1990-04-12"


def test_duplicate_email_is_rejected(client, staff_token, patient):
    response = client.post(
        "/patients/", headers=auth_header(staff_token), json=patient_payload()
    )

    assert response.status_code == 409


def test_duplicate_email_on_update_is_rejected(client, staff_token, patient, session):
    from app import crud, schemas

    other = crud.create_patient(
        session,
        schemas.PatientCreate(
            first_name="Other", last_name="Person", email="other@example.com"
        ),
    )

    response = client.put(
        f"/patients/{other.id}",
        headers=auth_header(staff_token),
        json={"email": patient.email},
    )

    assert response.status_code == 409


def test_keeping_your_own_email_on_update_is_fine(client, staff_token, patient):
    response = client.put(
        f"/patients/{patient.id}",
        headers=auth_header(staff_token),
        json={"email": patient.email, "address": "Bengaluru"},
    )

    assert response.status_code == 200
    assert response.json()["address"] == "Bengaluru"


def test_update_patient_is_partial(client, staff_token, patient):
    """A PATCH-shaped body must not blank out the fields it omits."""

    response = client.put(
        f"/patients/{patient.id}",
        headers=auth_header(staff_token),
        json={"phone": "+919000000000"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+919000000000"
    assert body["first_name"] == "Meera"
    assert body["email"] == "meera.rao@example.com"


def test_blank_name_is_rejected(client, staff_token):
    response = client.post(
        "/patients/", headers=auth_header(staff_token), json=patient_payload(first_name="   ")
    )

    assert response.status_code == 422


def test_whitespace_only_phone_is_treated_as_absent(client, staff_token):
    response = client.post(
        "/patients/", headers=auth_header(staff_token), json=patient_payload(phone="   ")
    )

    # Pydantic rejects it as a pattern mismatch rather than storing "   ".
    assert response.status_code == 422


def test_invalid_date_of_birth_is_rejected(client, staff_token):
    response = client.post(
        "/patients/",
        headers=auth_header(staff_token),
        json=patient_payload(date_of_birth="12-04-1990"),
    )

    assert response.status_code == 422


def test_pagination_bounds_are_honoured(client, staff_token, session):
    from app import crud, schemas

    for index in range(5):
        crud.create_patient(
            session,
            schemas.PatientCreate(
                first_name=f"Patient{index}",
                last_name="Test",
                email=f"p{index}@example.com",
            ),
        )

    response = client.get(
        "/patients/?skip=1&limit=2", headers=auth_header(staff_token)
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# ------------------------------------------------------------- appointments


def appointment_payload(patient_id, when):
    return {
        "patient_id": patient_id,
        "appointment_date": when,
        "duration_minutes": 45,
        "doctor_notes": "Follow-up on acidity.",
    }


def test_create_appointment(client, staff_token, patient, future_datetime):
    response = client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(patient.id, future_datetime.isoformat()),
    )

    assert response.status_code == 201, response.text
    assert response.json()["status"] == "pending"
    assert response.json()["duration_minutes"] == 45


def test_appointment_for_a_missing_patient_is_rejected(
    client, staff_token, future_datetime
):
    response = client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(9999, future_datetime.isoformat()),
    )

    assert response.status_code == 404
    assert "patient" in response.json()["detail"].lower()


@pytest.mark.parametrize("duration", [0, 5, 500])
def test_absurd_durations_are_rejected(
    client, staff_token, patient, future_datetime, duration
):
    response = client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(patient.id, future_datetime.isoformat())
        | {"duration_minutes": duration},
    )

    assert response.status_code == 422


def test_appointments_can_be_filtered_by_patient(
    client, staff_token, patient, future_datetime
):
    client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(patient.id, future_datetime.isoformat()),
    )

    response = client.get(
        f"/appointments/?patient_id={patient.id}", headers=auth_header(staff_token)
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_patient_appointments_route(client, staff_token, patient, future_datetime):
    client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(patient.id, future_datetime.isoformat()),
    )

    response = client.get(
        f"/patients/{patient.id}/appointments", headers=auth_header(staff_token)
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_deleting_a_patient_cascades_to_their_appointments(
    client, session, staff_token, patient, future_datetime
):
    """The reason patient_id became a real foreign key with ON DELETE CASCADE."""

    from app import crud

    created = client.post(
        "/appointments/",
        headers=auth_header(staff_token),
        json=appointment_payload(patient.id, future_datetime.isoformat()),
    )
    appointment_id = created.json()["id"]

    response = client.delete(
        f"/patients/{patient.id}", headers=auth_header(staff_token)
    )
    assert response.status_code == 204

    assert crud.get_appointment(session, appointment_id) is None


def test_missing_patient_returns_404(client, staff_token):
    assert (
        client.get("/patients/4242", headers=auth_header(staff_token)).status_code == 404
    )
    assert (
        client.get("/bookings/4242", headers=auth_header(staff_token)).status_code == 404
    )
    assert (
        client.get(
            "/appointments/4242", headers=auth_header(staff_token)
        ).status_code
        == 404
    )
