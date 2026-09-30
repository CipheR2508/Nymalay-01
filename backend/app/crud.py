"""Database access. All SQL lives here, behind ORM queries.

Note the move from `model.dict()` to `model.model_dump()`: `.dict()` is
deprecated in Pydantic v2 and emits a warning on every call.
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def normalise_phone(phone: str | None) -> str | None:
    """Reduce a phone number to its digits for comparison.

    The same person is written down as "+91 90000 00003", "090000 00003" and
    "919000000003" depending on who typed it. Comparing raw strings would create
    three patients and three appointments for one person. The last 10 digits are
    kept, which is the Indian mobile number and is what actually identifies the
    caller.
    """

    if not phone:
        return None
    digits = "".join(ch for ch in phone if ch.isdigit())
    if not digits:
        return None
    return digits[-10:] if len(digits) > 10 else digits


# --------------------------------------------------------------------- patient


def get_patient(db: Session, patient_id: int):
    return db.get(models.Patient, patient_id)


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.execute(
            select(models.Patient).order_by(models.Patient.id).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )


def get_patient_by_email(db: Session, email: str | None):
    if not email:
        return None
    return db.execute(
        select(models.Patient).where(models.Patient.email == email)
    ).scalars().first()


def get_patient_by_phone(db: Session, phone: str | None):
    """Look a patient up by phone, tolerating formatting differences."""
    if not phone:
        return None
    target = normalise_phone(phone)
    if not target:
        return None
    # The column stores the number as typed, so compare in Python. Fine at
    # clinic scale; if the patient table ever grew large, store a normalised
    # column alongside it and index that instead.
    candidates = db.execute(
        select(models.Patient).where(models.Patient.phone.is_not(None))
    ).scalars()
    for patient in candidates:
        if normalise_phone(patient.phone) == target:
            return patient
    return None


def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if db_patient is None:
        return None

    for field, value in patient.model_dump(exclude_unset=True).items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if db_patient is None:
        return None
    # Appointments cascade at the database level; SQLite needs FKs turned on.
    db.delete(db_patient)
    db.commit()
    return db_patient


# ------------------------------------------------------------------------ user


def get_user_by_username(db: Session, username: str):
    return db.execute(
        select(models.User).where(models.User.username == username)
    ).scalar_one_or_none()


def get_user_by_email(db: Session, email: str):
    return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()


def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.execute(select(models.User).order_by(models.User.id).offset(skip).limit(limit))
        .scalars()
        .all()
    )


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_admin=user.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --------------------------------------------------------------------- booking


def get_booking(db: Session, booking_id: int):
    return db.get(models.Booking, booking_id)


def get_bookings(
    db: Session,
    status: models.BookingStatus | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(models.Booking)
    if status is not None:
        query = query.where(models.Booking.status == status)
    return (
        db.execute(query.order_by(models.Booking.created_at.desc()).offset(skip).limit(limit))
        .scalars()
        .all()
    )


def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def update_booking_status(
    db: Session, booking_id: int, status: models.BookingStatus
):
    db_booking = get_booking(db, booking_id)
    if db_booking is None:
        return None
    db_booking.status = status
    db.commit()
    db.refresh(db_booking)
    return db_booking


# ----------------------------------------------------------------- appointment


def get_appointment(db: Session, appointment_id: int):
    return db.get(models.Appointment, appointment_id)


def get_appointments(
    db: Session,
    patient_id: int | None = None,
    status: models.AppointmentStatus | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(models.Appointment)
    if patient_id is not None:
        query = query.where(models.Appointment.patient_id == patient_id)
    if status is not None:
        query = query.where(models.Appointment.status == status)
    # Naive wall-clock comparison, consistent with how appointment_date is
    # stored. Lets the staff screen ask for "this week" without timezone maths.
    if from_datetime is not None:
        query = query.where(models.Appointment.appointment_date >= from_datetime)
    if to_datetime is not None:
        query = query.where(models.Appointment.appointment_date < to_datetime)
    return (
        db.execute(query.order_by(models.Appointment.appointment_date).offset(skip).limit(limit))
        .scalars()
        .all()
    )


def get_patient_appointments(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return get_appointments(db, patient_id=patient_id, skip=skip, limit=limit)


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def update_appointment(
    db: Session, appointment_id: int, appointment: schemas.AppointmentUpdate
):
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment is None:
        return None

    for field, value in appointment.model_dump(exclude_unset=True).items():
        setattr(db_appointment, field, value)

    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def delete_appointment(db: Session, appointment_id: int):
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment is None:
        return None
    db.delete(db_appointment)
    db.commit()
    return db_appointment


# ------------------------------------------------------------------ scheduling


def find_conflicting_appointment(
    db: Session,
    start: datetime,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
):
    """Return an appointment that overlaps the proposed slot, if any.

    There is one consultant, so any overlap at all is a double booking. The test
    is the standard half-open interval check:

        existing.start < proposed_end  AND  proposed_start < existing.end

    which lets a 10:00-10:45 and a 10:45-11:30 sit back to back without
    colliding, because 10:45 is not before 10:45.

    Cancelled appointments are ignored, so a cancelled slot is genuinely free.
    """

    proposed_end = start + timedelta(minutes=duration_minutes)

    candidates = db.execute(
        select(models.Appointment).where(
            models.Appointment.status != models.AppointmentStatus.CANCELLED,
            # Cheap bounds first so the interval test only runs on same-day rows.
            models.Appointment.appointment_date < proposed_end,
            models.Appointment.appointment_date
            >= start - timedelta(minutes=180),
        )
    ).scalars()

    for existing in candidates:
        if exclude_appointment_id is not None and existing.id == exclude_appointment_id:
            continue
        existing_end = existing.appointment_date + timedelta(
            minutes=existing.duration_minutes
        )
        if existing.appointment_date < proposed_end and start < existing_end:
            return existing
    return None


def find_or_create_patient(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    phone: str | None,
    email: str | None,
    date_of_birth=None,
) -> tuple[models.Patient, bool]:
    """Reuse an existing patient where possible, otherwise create one.

    Returns `(patient, reused)`. Phone is checked first because that is what the
    public form collects and what patients recognise; email is the fallback.

    Callers must not commit; this is a step inside a larger transaction.
    """

    existing = get_patient_by_phone(db, phone) or get_patient_by_email(db, email)
    if existing is not None:
        # Fill in gaps rather than overwriting: staff may add an email that was
        # never collected on the form, and clobbering a known address with a
        # blank one loses data.
        changed = False
        if email and not existing.email:
            existing.email = email
            changed = True
        if date_of_birth and not existing.date_of_birth:
            existing.date_of_birth = date_of_birth
            changed = True
        if changed:
            db.add(existing)
        return existing, True

    patient = models.Patient(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        date_of_birth=date_of_birth,
    )
    db.add(patient)
    # Flush rather than commit so the row gets an id and any unique-violation
    # surfaces here, inside the caller's transaction.
    db.flush()
    return patient, False


def schedule_booking(
    db: Session,
    booking: models.Booking,
    request: schemas.ScheduleBookingRequest,
) -> tuple[models.Booking, models.Patient, models.Appointment, bool]:
    """Convert a booking request into a scheduled appointment, atomically.

    Creates or reuses the patient, reserves the slot, links the booking and
    marks it confirmed - all in one transaction, so a clash halfway through
    cannot leave a half-created patient and an orphaned booking behind.

    Callers must commit. Raises ValueError for a booking that cannot be
    scheduled; the route turns that into a 409.
    """

    if booking.status == models.BookingStatus.CANCELLED:
        raise ValueError("this booking was cancelled and cannot be scheduled")
    if booking.patient_id is not None:
        raise ValueError("this booking has already been scheduled")

    clash = find_conflicting_appointment(
        db, request.appointment_date, request.duration_minutes
    )
    if clash is not None:
        raise ValueError(
            "that slot overlaps an existing appointment at "
            f"{clash.appointment_date.strftime('%d %b %Y, %H:%M')}"
        )

    patient, reused = find_or_create_patient(
        db,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone or booking.phone,
        email=request.email or booking.email,
        date_of_birth=request.date_of_birth,
    )

    appointment = models.Appointment(
        patient_id=patient.id,
        appointment_date=request.appointment_date,
        duration_minutes=request.duration_minutes,
        status=models.AppointmentStatus.CONFIRMED,
        doctor_notes=request.doctor_notes,
    )
    db.add(appointment)

    booking.patient_id = patient.id
    booking.status = models.BookingStatus.CONFIRMED
    # Carry an email the form never asked for onto the booking too, so the
    # record is self-contained.
    if request.email and not booking.email:
        booking.email = request.email
    db.add(booking)

    db.flush()
    return booking, patient, appointment, reused
