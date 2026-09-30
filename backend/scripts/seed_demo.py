"""Seed a staff account and sample records for local development.

The app already creates one admin on first boot from ADMIN_USERNAME /
ADMIN_EMAIL / ADMIN_PASSWORD (see main.seed_admin_if_missing). This script is
for the rest of the demo data: a staff user, two patients, appointments and a
couple of booking requests, so the staff screens have something to render.

    python scripts/seed_demo.py
    python scripts/seed_demo.py --reset     # wipe first

Refuses to run when ENVIRONMENT=production, and prints the credentials it
creates so they are not mistaken for real ones.
"""

import argparse
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

# Allow `python scripts/seed_demo.py` from the backend directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import crud, models, schemas  # noqa: E402
from app.auth import get_password_hash  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402

STAFF_USERNAME = "staff.demo"
STAFF_PASSWORD = "demo-staff-pass-1"
STAFF_EMAIL = "staff.demo@nymalay.clinic"


def wipe(session) -> None:
    """Remove demo rows, leaving anything real alone.

    Appointments and bookings first: they hold foreign keys to patients.
    """
    for model in (
        models.Appointment,
        models.Booking,
        models.Patient,
        models.User,
    ):
        session.query(model).delete()
    session.commit()
    print("cleared appointments, bookings, patients and users")


def seed(session) -> None:
    if crud.get_user_by_username(session, STAFF_USERNAME):
        print(f"user '{STAFF_USERNAME}' already exists, nothing to do")
        return

    crud.create_user(
        session,
        schemas.UserCreate(
            username=STAFF_USERNAME,
            email=STAFF_EMAIL,
            full_name="Demo Staff",
            password=STAFF_PASSWORD,
        ),
        get_password_hash(STAFF_PASSWORD),
    )
    print(f"user: {STAFF_USERNAME} / {STAFF_PASSWORD}")

    first = crud.create_patient(
        session,
        schemas.PatientCreate(
            first_name="Asha",
            last_name="Menon",
            email="asha.menon@example.com",
            phone="+91 90000 00001",
            date_of_birth=date(1988, 4, 12),
            address="12 MG Road, Pune",
            medical_history="Seasonal allergic rhinitis. No known drug allergies.",
        ),
    )
    second = crud.create_patient(
        session,
        schemas.PatientCreate(
            first_name="Ravi",
            last_name="Deshpande",
            email="ravi.deshpande@example.com",
            phone="+91 90000 00002",
            date_of_birth=date(1976, 11, 3),
        ),
    )
    print(f"patients: #{first.id} {first.first_name} {first.last_name}, "
          f"#{second.id} {second.first_name} {second.last_name}")

    today = date.today()
    crud.create_appointment(
        session,
        schemas.AppointmentCreate(
            patient_id=first.id,
            appointment_date=datetime.combine(
                today + timedelta(days=3), time(10, 30)
            ),
            duration_minutes=45,
            doctor_notes="First consultation. Bring current medication list.",
        ),
    )
    crud.create_appointment(
        session,
        schemas.AppointmentCreate(
            patient_id=second.id,
            appointment_date=datetime.combine(
                today + timedelta(days=7), time(16, 0)
            ),
            duration_minutes=30,
        ),
    )
    print("appointments: 2 scheduled")

    crud.create_booking(
        session,
        schemas.BookingCreate(
            name="Sunita Kulkarni",
            phone="+91 90000 00003",
            preferred_date=today + timedelta(days=2),
            concern="Recurring headaches, roughly once a week for two months.",
        ),
    )
    crud.create_booking(
        session,
        schemas.BookingCreate(
            name="Imran Shaikh",
            phone="+91 90000 00004",
            preferred_date=today + timedelta(days=5),
            concern="Sleep disturbance and low energy since a change of job.",
        ),
    )
    print("bookings: 2 new requests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete existing rows before seeding",
    )
    args = parser.parse_args()

    if settings.is_production:
        print("refusing to seed: ENVIRONMENT is 'production'")
        return 1
    if not settings.is_sqlite:
        print(
            "refusing to seed a shared database without an explicit --force; "
            f"DATABASE_URL is {settings.DATABASE_URL.split('@')[-1]}"
        )
        return 1

    print(f"seeding {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        if args.reset:
            wipe(session)
        seed(session)

    print("\ndone. log in at POST /token with the credentials above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
