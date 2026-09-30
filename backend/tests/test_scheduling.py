"""Booking -> patient -> appointment scheduling.

This is the path that turns a public request into a real consultation, so the
tests here are mostly about the ways it can go wrong: two patients in one slot,
a booking scheduled twice, a patient duplicated because their phone number was
typed with different spacing, and a clash that must not leave half a record
behind.
"""

from datetime import date, datetime, time, timedelta

import pytest

from conftest import auth_header
from tests.test_bookings import booking_payload

TOMORROW = date.today() + timedelta(days=1)


def slot(days_ahead=1, hour=10, minute=0):
    """A naive local wall-clock slot, matching how the API stores them."""
    target = date.today() + timedelta(days=days_ahead)
    return datetime(target.year, target.month, target.day, hour, minute).isoformat()


def schedule_payload(**overrides):
    payload = {
        "appointment_date": slot(),
        "duration_minutes": 45,
        "first_name": "Sunita",
        "last_name": "Kulkarni",
        "phone": "+91 90000 00003",
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def new_booking(client):
    response = client.post("/bookings/", json=booking_payload())
    assert response.status_code == 201
    return response.json()


# ----------------------------------------------------------------- happy path


def test_scheduling_a_booking_creates_patient_and_appointment(
    client, staff_token, new_booking
):
    response = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )

    assert response.status_code == 201
    body = response.json()

    assert body["booking"]["status"] == "confirmed"
    assert body["booking"]["patient_id"] == body["patient"]["id"]
    assert body["patient"]["first_name"] == "Sunita"
    assert body["patient"]["last_name"] == "Kulkarni"
    assert body["appointment"]["status"] == "confirmed"
    assert body["appointment"]["duration_minutes"] == 45
    assert body["appointment"]["patient_id"] == body["patient"]["id"]
    assert body["reused_patient"] is False


def test_scheduled_appointment_shows_up_in_the_appointment_list(
    client, staff_token, new_booking
):
    client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )

    listed = client.get("/appointments/", headers=auth_header(staff_token))

    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_patient_email_is_optional_on_the_booking_form(client, staff_token):
    """A two-field form must not require an email address."""

    payload = booking_payload()
    payload.pop("email", None)

    created = client.post("/bookings/", json=payload)
    assert created.status_code == 201
    assert created.json()["email"] is None

    scheduled = client.post(
        f"/bookings/{created.json()['id']}/schedule",
        # No phone supplied here, so it must fall back to the booking's.
        json={
            "appointment_date": slot(),
            "duration_minutes": 45,
            "first_name": "Sunita",
            "last_name": "Kulkarni",
        },
        headers=auth_header(staff_token),
    )
    assert scheduled.status_code == 201
    # The booking's own phone is used as the patient's phone.
    assert scheduled.json()["patient"]["phone"] == payload["phone"]


def test_booking_email_is_carried_into_the_patient_record(client, staff_token):
    created = client.post(
        "/bookings/", json=booking_payload(email="sunita@example.com")
    )
    booking = created.json()

    scheduled = client.post(
        f"/bookings/{booking['id']}/schedule",
        json=schedule_payload(first_name="Sunita", last_name="Kulkarni"),
        headers=auth_header(staff_token),
    )

    assert scheduled.status_code == 201
    assert scheduled.json()["patient"]["email"] == "sunita@example.com"


# --------------------------------------------------------------- double booking


def test_overlapping_slot_is_refused(client, staff_token, new_booking):
    first = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    assert first.status_code == 201

    second = client.post("/bookings/", json=booking_payload(name="Other Person"))
    clash = client.post(
        f"/bookings/{second.json()['id']}/schedule",
        # 10:30 sits inside the first 10:00-10:45 appointment.
        json=schedule_payload(
            appointment_date=slot(hour=10, minute=30),
            first_name="Other",
            last_name="Person",
        ),
        headers=auth_header(staff_token),
    )

    assert clash.status_code == 409
    assert "overlaps" in clash.json()["detail"].lower()


def test_back_to_back_appointments_are_allowed(client, staff_token, new_booking):
    """10:00-10:45 then 10:45-11:30 is a normal clinic day, not a clash."""

    first = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    assert first.status_code == 201

    second = client.post("/bookings/", json=booking_payload(name="Other Person"))
    adjacent = client.post(
        f"/bookings/{second.json()['id']}/schedule",
        json=schedule_payload(
            appointment_date=slot(hour=10, minute=45),
            first_name="Other",
            last_name="Person",
        ),
        headers=auth_header(staff_token),
    )

    assert adjacent.status_code == 201


def test_cancelled_appointment_frees_its_slot(client, staff_token, new_booking):
    scheduled = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    appointment_id = scheduled.json()["appointment"]["id"]

    cancelled = client.put(
        f"/appointments/{appointment_id}",
        json={"status": "cancelled"},
        headers=auth_header(staff_token),
    )
    assert cancelled.status_code == 200

    second = client.post("/bookings/", json=booking_payload(name="Later Patient"))
    reuse = client.post(
        f"/bookings/{second.json()['id']}/schedule",
        json=schedule_payload(first_name="Later", last_name="Patient"),
        headers=auth_header(staff_token),
    )

    assert reuse.status_code == 201


def test_a_refused_clash_leaves_nothing_behind(client, staff_token, new_booking):
    """The losing side of a clash must not create a patient or appointment."""

    taken = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    assert taken.status_code == 201

    other = client.post("/bookings/", json=booking_payload(name="Clash Person"))
    clash = client.post(
        f"/bookings/{other.json()['id']}/schedule",
        json=schedule_payload(
            appointment_date=slot(hour=10, minute=10),
            first_name="Clash",
            last_name="Person",
        ),
        headers=auth_header(staff_token),
    )
    assert clash.status_code == 409

    # Still exactly one appointment, from the winner only.
    appointments = client.get("/appointments/", headers=auth_header(staff_token)).json()
    assert len(appointments) == 1

    # The refused booking is untouched: still unconfirmed, still unlinked.
    still = client.get(
        f"/bookings/{other.json()['id']}", headers=auth_header(staff_token)
    ).json()
    assert still["status"] == "new"
    assert still["patient_id"] is None

    # And the loser's patient was not persisted.
    patients = client.get("/patients/", headers=auth_header(staff_token)).json()
    assert [p["first_name"] for p in patients] == ["Sunita"]


# ---------------------------------------------------------------- idempotency


def test_a_booking_cannot_be_scheduled_twice(client, staff_token, new_booking):
    first = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    assert first.status_code == 201

    repeat = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(appointment_date=slot(hour=14)),
        headers=auth_header(staff_token),
    )

    assert repeat.status_code == 409
    assert "already been scheduled" in repeat.json()["detail"]


def test_cancelled_booking_cannot_be_scheduled(client, staff_token, new_booking):
    client.patch(
        f"/bookings/{new_booking['id']}",
        json={"status": "cancelled"},
        headers=auth_header(staff_token),
    )

    response = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )

    assert response.status_code == 409
    assert "cancelled" in response.json()["detail"]


# ---------------------------------------------------------------- dedupe rules


def test_existing_patient_is_reused_rather_than_duplicated(client, staff_token, new_booking):
    first = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    patient_id = first.json()["patient"]["id"]

    second = client.post("/bookings/", json=booking_payload(name="Sunita Again"))
    repeat = client.post(
        f"/bookings/{second.json()['id']}/schedule",
        json=schedule_payload(appointment_date=slot(hour=15)),
        headers=auth_header(staff_token),
    )

    assert repeat.status_code == 201
    assert repeat.json()["reused_patient"] is True
    assert repeat.json()["patient"]["id"] == patient_id

    patients = client.get("/patients/", headers=auth_header(staff_token)).json()
    assert len(patients) == 1


def test_phone_formatting_does_not_create_a_second_patient(client, staff_token, new_booking):
    """Same human, three ways of writing the number."""

    first = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(phone="+91 90000 00003"),
        headers=auth_header(staff_token),
    )
    assert first.json()["reused_patient"] is False

    second = client.post("/bookings/", json=booking_payload(name="Sunita Again"))
    repeat = client.post(
        f"/bookings/{second.json()['id']}/schedule",
        json=schedule_payload(phone="919000000003", appointment_date=slot(hour=16)),
        headers=auth_header(staff_token),
    )

    assert repeat.status_code == 201
    assert repeat.json()["reused_patient"] is True

    patients = client.get("/patients/", headers=auth_header(staff_token)).json()
    assert len(patients) == 1


def test_staff_email_fills_a_gap_without_overwriting(client, staff_token, new_booking):
    existing = client.post(
        "/patients/",
        json={
            "first_name": "Sunita",
            "last_name": "Kulkarni",
            "phone": "+91 90000 00003",
        },
        headers=auth_header(staff_token),
    )
    assert existing.status_code == 201

    scheduled = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(email="sunita@example.com"),
        headers=auth_header(staff_token),
    )

    assert scheduled.status_code == 201
    assert scheduled.json()["reused_patient"] is True
    assert scheduled.json()["patient"]["email"] == "sunita@example.com"


# ------------------------------------------------------------------- access


def test_scheduling_requires_a_staff_token(client, new_booking):
    anonymous = client.post(
        f"/bookings/{new_booking['id']}/schedule", json=schedule_payload()
    )
    assert anonymous.status_code == 401

    bogus = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(),
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert bogus.status_code == 401


def test_scheduling_a_missing_booking_is_404(client, staff_token):
    response = client.post(
        "/bookings/999999/schedule",
        json=schedule_payload(),
        headers=auth_header(staff_token),
    )
    assert response.status_code == 404


# ----------------------------------------------------------------- validation


def test_past_appointment_date_is_rejected(client, staff_token, new_booking):
    past = datetime.now() - timedelta(days=1)

    response = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(appointment_date=past.isoformat()),
        headers=auth_header(staff_token),
    )

    assert response.status_code == 422


def test_absurd_duration_is_rejected(client, staff_token, new_booking):
    response = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(duration_minutes=600),
        headers=auth_header(staff_token),
    )

    assert response.status_code == 422


def test_blank_patient_name_is_rejected(client, staff_token, new_booking):
    response = client.post(
        f"/bookings/{new_booking['id']}/schedule",
        json=schedule_payload(first_name="   "),
        headers=auth_header(staff_token),
    )

    assert response.status_code == 422


# --------------------------------------------------- the whole patient journey


def test_request_to_consultation_end_to_end(client, staff_token):
    """What a real booking looks like, start to finish."""

    # 1. Patient fills in the public form. No account, no token.
    requested = client.post(
        "/bookings/",
        json={
            "name": "Imran Shaikh",
            "phone": "91900000004",
            "preferred_date": TOMORROW.isoformat(),
            "concern": "Sleep disturbance and low energy for about two months.",
        },
    )
    assert requested.status_code == 201
    booking_id = requested.json()["id"]

    # 2. Staff mark it as contacted.
    contacted = client.patch(
        f"/bookings/{booking_id}",
        json={"status": "contacted"},
        headers=auth_header(staff_token),
    )
    assert contacted.json()["status"] == "contacted"

    # 3. Staff agree a slot on the phone and schedule it.
    confirmed = client.post(
        f"/bookings/{booking_id}/schedule",
        json={
            "appointment_date": slot(days_ahead=2, hour=16, minute=0),
            "duration_minutes": 45,
            "first_name": "Imran",
            "last_name": "Shaikh",
            "date_of_birth": date(1990, 6, 15).isoformat(),
            "doctor_notes": "Bring sleep log if available.",
        },
        headers=auth_header(staff_token),
    )
    assert confirmed.status_code == 201
    body = confirmed.json()

    # 4. The patient now has a real record reachable from the appointment.
    patient_id = body["patient"]["id"]
    record = client.get(f"/patients/{patient_id}", headers=auth_header(staff_token))
    assert record.status_code == 200
    assert record.json()["date_of_birth"] == "1990-06-15"

    # 5. And their appointment shows under that patient.
    appointments = client.get(
        f"/patients/{patient_id}/appointments", headers=auth_header(staff_token)
    )
    assert len(appointments.json()) == 1
    assert appointments.json()[0]["status"] == "confirmed"

    # 6. The public booking shows as confirmed and linked.
    final = client.get(f"/bookings/{booking_id}", headers=auth_header(staff_token)).json()
    assert final["status"] == "confirmed"
    assert final["patient_id"] == patient_id
