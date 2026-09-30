"""Booking endpoint tests - the contract the website form depends on.

The payloads here are copied from what components/BookingForm.js actually
sends. If one side changes, these should fail.
"""

import pytest
from conftest import auth_header


def booking_payload(**overrides):
    from datetime import date, timedelta

    payload = {
        "name": "Anita Sharma",
        "phone": "+919876543210",
        "preferred_date": (date.today() + timedelta(days=5)).isoformat(),
        "concern": "Recurring acidity for the past six months, worse after meals.",
    }
    payload.update(overrides)
    return payload


def test_public_booking_is_accepted_without_a_token(client):
    """The website form has no session, so this route must stay open."""

    response = client.post("/bookings/", json=booking_payload())

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "new"
    assert body["name"] == "Anita Sharma"
    assert body["id"] > 0


def test_booking_is_persisted(client, session):
    from app import crud

    client.post("/bookings/", json=booking_payload())

    stored = crud.get_bookings(session)
    assert len(stored) == 1
    assert stored[0].phone == "+919876543210"


@pytest.mark.parametrize(
    "override,expected_fragment",
    [
        ({"name": ""}, "name"),
        ({"name": "A"}, "name"),
        ({"phone": "not-a-phone"}, "phone"),
        ({"phone": "12345"}, "phone"),
        ({"concern": "short"}, "concern"),
    ],
)
def test_booking_rejects_bad_input(client, override, expected_fragment):
    response = client.post("/bookings/", json=booking_payload(**override))

    assert response.status_code == 422, response.text
    assert expected_fragment in response.text.lower()


def test_booking_rejects_a_past_date(client):
    from datetime import date, timedelta

    response = client.post(
        "/bookings/",
        json=booking_payload(preferred_date=(date.today() - timedelta(days=1)).isoformat()),
    )

    assert response.status_code == 422


def test_booking_today_is_allowed(client):
    from datetime import date

    response = client.post(
        "/bookings/", json=booking_payload(preferred_date=date.today().isoformat())
    )

    assert response.status_code == 201


def test_booking_response_does_not_echo_anything_unexpected(client):
    response = client.post("/bookings/", json=booking_payload())

    assert set(response.json()) == {
        "id",
        "name",
        "phone",
        "email",
        "preferred_date",
        "concern",
        "status",
        "patient_id",
        "created_at",
        "updated_at",
    }


def test_booking_appears_in_the_staff_queue(client, staff_token):
    from datetime import date, timedelta

    created = client.post(
        "/bookings/",
        json=booking_payload(preferred_date=(date.today() + timedelta(days=3)).isoformat()),
    )
    booking_id = created.json()["id"]

    listing = client.get("/bookings/", headers=auth_header(staff_token))
    assert listing.status_code == 200
    assert [b["id"] for b in listing.json()] == [booking_id]

    detail = client.get(f"/bookings/{booking_id}", headers=auth_header(staff_token))
    assert detail.status_code == 200
    assert detail.json()["status"] == "new"


def test_staff_can_advance_a_booking_to_contacted(client, staff_token):
    created = client.post("/bookings/", json=booking_payload())
    booking_id = created.json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}",
        headers=auth_header(staff_token),
        json={"status": "contacted"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "contacted"


def test_booking_status_rejects_a_value_outside_the_enum(client, staff_token):
    created = client.post("/bookings/", json=booking_payload())
    booking_id = created.json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}",
        headers=auth_header(staff_token),
        json={"status": "teleported"},
    )

    assert response.status_code == 422
