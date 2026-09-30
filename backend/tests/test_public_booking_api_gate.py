"""The deployed site's actual configuration: the booking API is off.

The public website hands a consultation request to WhatsApp or email and books
nothing, so the landing-page deployment runs with these routes closed. These
tests are the counterpart to test_bookings.py and test_scheduling.py, which
cover the same code with the gate opened by conftest.

A 404 is asserted rather than a 403 on purpose: from the public internet these
endpoints should be indistinguishable from endpoints that do not exist.
"""

import pytest
from conftest import STAFF_PASSWORD, auth_header, login


@pytest.fixture()
def closed_api(monkeypatch):
    """Close the gate for the duration of one test."""

    from app import main

    monkeypatch.setattr(main.settings, "ENABLE_LEGACY_BOOKING_API", False)
    return main.settings


def test_health_reports_the_gate_is_closed(client, closed_api):
    response = client.get("/health")

    assert response.status_code == 200, response.text
    assert response.json()["legacy_booking_api"] is False


def test_public_booking_route_does_not_exist(client, closed_api):
    """The one route that never needed a token must 404, not accept a booking."""

    response = client.post(
        "/bookings/",
        json={
            "name": "Anita Sharma",
            "phone": "+919876543210",
            "preferred_date": "2030-01-15",
            "concern": "Recurring acidity for the past six months.",
        },
    )

    assert response.status_code == 404, response.text
    assert "whatsapp" in response.text.lower()


def test_no_booking_record_is_written_when_closed(client, session, closed_api):
    from app import crud

    client.post(
        "/bookings/",
        json={
            "name": "Anita Sharma",
            "phone": "+919876543210",
            "preferred_date": "2030-01-15",
            "concern": "Recurring acidity for the past six months.",
        },
    )

    assert crud.get_bookings(session) == []


def test_booking_queue_is_hidden_even_from_staff(client, staff, closed_api):
    token = login(client, "drarya", STAFF_PASSWORD)

    response = client.get("/bookings/", headers=auth_header(token))

    assert response.status_code == 404, response.text


def test_scheduling_is_blocked_even_for_an_existing_request(client, staff, monkeypatch):
    """A request captured while the API was open can no longer be confirmed."""

    from app import main

    token = login(client, "drarya", STAFF_PASSWORD)
    booking = client.post(
        "/bookings/",
        json={
            "name": "Anita Sharma",
            "phone": "+919876543210",
            "preferred_date": "2030-01-15",
            "concern": "Recurring acidity for the past six months.",
        },
    )
    booking_id = booking.json()["id"]

    monkeypatch.setattr(main.settings, "ENABLE_LEGACY_BOOKING_API", False)
    response = client.post(
        f"/bookings/{booking_id}/schedule",
        json={"appointment_datetime": "2030-01-15T10:00:00"},
        headers=auth_header(token),
    )

    # The gate runs as a dependency, so it wins over the body: nothing is
    # validated or written.
    assert response.status_code == 404, response.text


def test_status_change_is_blocked_too(client, staff, monkeypatch):
    from app import main

    token = login(client, "drarya", STAFF_PASSWORD)
    booking = client.post(
        "/bookings/",
        json={
            "name": "Anita Sharma",
            "phone": "+919876543210",
            "preferred_date": "2030-01-15",
            "concern": "Recurring acidity for the past six months.",
        },
    )
    booking_id = booking.json()["id"]

    monkeypatch.setattr(main.settings, "ENABLE_LEGACY_BOOKING_API", False)
    response = client.patch(
        f"/bookings/{booking_id}",
        json={"status": "confirmed"},
        headers=auth_header(token),
    )

    assert response.status_code == 404, response.text


def test_appointments_are_unreachable(client, staff, patient, closed_api):
    token = login(client, "drarya", STAFF_PASSWORD)

    created = client.post(
        "/appointments/",
        json={
            "patient_id": patient.id,
            "appointment_datetime": "2030-01-15T10:00:00",
            "duration_minutes": 60,
            "status": "scheduled",
        },
        headers=auth_header(token),
    )
    listed = client.get("/appointments/", headers=auth_header(token))
    by_patient = client.get(
        f"/patients/{patient.id}/appointments", headers=auth_header(token)
    )

    assert created.status_code == 404, created.text
    assert listed.status_code == 404, listed.text
    assert by_patient.status_code == 404, by_patient.text


def test_patient_records_still_work_while_the_booking_api_is_closed(
    client, staff, closed_api
):
    """The gate must not take the patient register down with it."""

    token = login(client, "drarya", STAFF_PASSWORD)

    response = client.get("/patients/", headers=auth_header(token))

    assert response.status_code == 200, response.text


def test_gate_reopens_with_the_environment_flag(client, monkeypatch, staff):
    """Sanity check on the other side: the flag is what turns it back on."""

    from app import main

    monkeypatch.setattr(main.settings, "ENABLE_LEGACY_BOOKING_API", True)

    response = client.post(
        "/bookings/",
        json={
            "name": "Anita Sharma",
            "phone": "+919876543210",
            "preferred_date": "2030-01-15",
            "concern": "Recurring acidity for the past six months.",
        },
    )

    assert response.status_code == 201, response.text
