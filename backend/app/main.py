"""Nymalay Homoeopathy API.

Status
------
The public website is a static landing page. It hands a consultation request to
WhatsApp or email and books nothing: the doctor reviews each request, assigns
the date and time, agrees the slot, verifies payment and confirms. The API below
is the earlier direct-booking system, kept intact for a future phase but
switched off by default.

Active with no flag set:
    GET  /health              liveness probe, reports whether the gate is open
    GET/PUT/DELETE /patients/...
    GET  /users/me
    GET  /users/  POST /users/   (admin)
    POST /token

Gated behind ENABLE_LEGACY_BOOKING_API=true, returning 404 otherwise:
    POST /bookings/           legacy website booking form
    GET/PATCH /bookings/...   request queue and lifecycle
    POST /bookings/{id}/schedule
    GET/POST/PUT/DELETE /appointments/...
    GET  /patients/{id}/appointments

All gated routes still require a Bearer staff token, except the legacy public
POST /bookings/. The gate is the second lock, not the only one.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .config import settings
from .database import Base, SessionLocal, engine, get_db


# ------------------------------------------------------------------- bootstrapping


def init_db() -> None:
    """Create tables that do not exist yet.

    Fine for SQLite/local and first boot. Postgres deployments should be moved
    onto Alembic (see docs/adr) before the schema starts changing.
    """

    Base.metadata.create_all(bind=engine)


def seed_admin_if_missing() -> None:
    """Create a first admin from env vars so staff login is reachable at all.

    No-op if any user already exists, or if ADMIN_PASSWORD is unset.
    """

    if not settings.ADMIN_PASSWORD:
        return

    db = SessionLocal()
    try:
        if crud.get_user_by_username(db, settings.ADMIN_USERNAME) is not None:
            return
        crud.create_user(
            db,
            schemas.UserCreate(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                full_name="Clinic Admin",
                password=settings.ADMIN_PASSWORD,
                is_admin=True,
            ),
            auth.get_password_hash(settings.ADMIN_PASSWORD),
        )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_admin_if_missing()
    yield


app = FastAPI(
    title="Nymalay Homoeopathy API",
    description=(
        "API for managing patient appointments, booking requests and records "
        "for Nymalay Homoeopathy."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

DbSession = Annotated[Session, Depends(get_db)]
StaffUser = Annotated[models.User, Depends(auth.get_current_staff)]
AdminUser = Annotated[models.User, Depends(auth.require_admin)]


def not_found(entity: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{entity} not found")


# ------------------------------------------------------------------- health


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "legacy_booking_api": settings.ENABLE_LEGACY_BOOKING_API,
    }


def require_legacy_booking_api() -> None:
    """Refuse the legacy booking routes unless they are explicitly enabled.

    The public site hands requests to WhatsApp or email and books nothing, so
    these routes have no caller. Leaving them open would mean a bookmarked URL
    or a stale client could still create a booking record and, through the
    dashboard, present it as an appointment the clinic never agreed to. A 404
    rather than a 403: from the public internet these endpoints are meant not to
    exist at all, and a 403 would confirm they do.

    Set ENABLE_LEGACY_BOOKING_API=true to re-enable them.
    """

    if settings.ENABLE_LEGACY_BOOKING_API:
        return
    raise HTTPException(
        status_code=404,
        detail=(
            "Not found. The clinic website no longer accepts bookings through an "
            "API: please use WhatsApp or email, or visit the website's "
            "consultation request form."
        ),
    )


# --------------------------------------------------------------------- auth


@app.post("/token", response_model=schemas.Token, tags=["auth"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Same message for unknown user, wrong password and inactive account.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User, tags=["auth"])
def read_current_user(current: StaffUser):
    return current


@app.get("/users/", response_model=list[schemas.User], tags=["users"])
def read_users(db: DbSession, _: AdminUser, skip: int = 0, limit: int = 100):
    return crud.get_users(db, skip=skip, limit=limit)


@app.post(
    "/users/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def create_user(user: schemas.UserCreate, db: DbSession, _: AdminUser):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    return crud.create_user(db, user, auth.get_password_hash(user.password))


# ----------------------------------------------------------------- patients
#
# Every route below returns protected health information, so all of them require
# a staff token. Before this change GET /patients/ was an open, unauthenticated
# dump of the clinic's patient records.


@app.post(
    "/patients/",
    response_model=schemas.Patient,
    status_code=status.HTTP_201_CREATED,
    tags=["patients"],
)
def create_patient(patient: schemas.PatientCreate, db: DbSession, _: StaffUser):
    if crud.get_patient_by_email(db, patient.email):
        raise HTTPException(status_code=409, detail="A patient with this email exists")
    return crud.create_patient(db=db, patient=patient)


@app.get("/patients/", response_model=list[schemas.Patient], tags=["patients"])
def read_patients(db: DbSession, _: StaffUser, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    return crud.get_patients(db, skip=skip, limit=limit)


@app.get("/patients/{patient_id}", response_model=schemas.Patient, tags=["patients"])
def read_patient(patient_id: int, db: DbSession, _: StaffUser):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise not_found("Patient")
    return db_patient


@app.put("/patients/{patient_id}", response_model=schemas.Patient, tags=["patients"])
def update_patient(
    patient_id: int, patient: schemas.PatientUpdate, db: DbSession, _: StaffUser
):
    if patient.email is not None:
        existing = crud.get_patient_by_email(db, patient.email)
        if existing is not None and existing.id != patient_id:
            raise HTTPException(status_code=409, detail="A patient with this email exists")

    db_patient = crud.update_patient(db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise not_found("Patient")
    return db_patient


@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["patients"])
def delete_patient(patient_id: int, db: DbSession, _: StaffUser):
    if crud.delete_patient(db, patient_id=patient_id) is None:
        raise not_found("Patient")
    return None


# ----------------------------------------------------------------- bookings
#
# Every route in this section is gated by `require_legacy_booking_api`, so all
# of them return 404 unless ENABLE_LEGACY_BOOKING_API=true. The public site
# books nothing, so these are unreachable in the landing-page deployment.


@app.post(
    "/bookings/",
    response_model=schemas.Booking,
    status_code=status.HTTP_201_CREATED,
    tags=["bookings"],
)
def create_booking(
    booking: schemas.BookingCreate, db: DbSession, __: None = Depends(require_legacy_booking_api)
):
    """Legacy public booking endpoint. Off by default; see the note above."""
    return crud.create_booking(db=db, booking=booking)


@app.get("/bookings/", response_model=list[schemas.Booking], tags=["bookings"])
def read_bookings(
    db: DbSession,
    _: StaffUser,
    status_filter: models.BookingStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    __: None = Depends(require_legacy_booking_api),
):
    return crud.get_bookings(db, status=status_filter, skip=skip, limit=limit)


@app.get("/bookings/{booking_id}", response_model=schemas.Booking, tags=["bookings"])
def read_booking(
    booking_id: int,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    db_booking = crud.get_booking(db, booking_id)
    if db_booking is None:
        raise not_found("Booking")
    return db_booking


@app.patch("/bookings/{booking_id}", response_model=schemas.Booking, tags=["bookings"])
def update_booking_status(
    booking_id: int,
    payload: schemas.BookingStatusUpdate,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    db_booking = crud.update_booking_status(db, booking_id, payload.status)
    if db_booking is None:
        raise not_found("Booking")
    return db_booking


@app.post(
    "/bookings/{booking_id}/schedule",
    response_model=schemas.ScheduledBooking,
    status_code=status.HTTP_201_CREATED,
    tags=["bookings"],
    summary="Turn a booking request into a confirmed appointment",
)
def schedule_booking(
    booking_id: int,
    payload: schemas.ScheduleBookingRequest,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    """Close the loop on a public request.

    Creates or reuses the patient, reserves the slot, links the booking and marks
    it confirmed in a single transaction, then hands back all three records so
    the staff screen can show the confirmed slot and message the patient without
    a second request.
    """

    db_booking = crud.get_booking(db, booking_id)
    if db_booking is None:
        raise not_found("Booking")

    try:
        booking, patient, appointment, reused = crud.schedule_booking(
            db, db_booking, payload
        )
        db.commit()
    except ValueError as exc:
        # Slot clash, already-scheduled or cancelled booking. Nothing was
        # written, so there is nothing to roll back.
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError as exc:
        # Lost a race on the unique patient phone/email index.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A patient with those contact details was just created. Reload and try again.",
        ) from exc

    for record in (booking, patient, appointment):
        db.refresh(record)

    return schemas.ScheduledBooking(
        booking=booking,
        patient=patient,
        appointment=appointment,
        reused_patient=reused,
    )


# ------------------------------------------------------------- appointments


@app.post(
    "/appointments/",
    response_model=schemas.Appointment,
    status_code=status.HTTP_201_CREATED,
    tags=["appointments"],
)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    if crud.get_patient(db, appointment.patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_appointment(db=db, appointment=appointment)


@app.get("/appointments/", response_model=list[schemas.Appointment], tags=["appointments"])
def read_appointments(
    db: DbSession,
    _: StaffUser,
    patient_id: int | None = None,
    status_filter: models.AppointmentStatus | None = Query(None, alias="status"),
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None, alias="to"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    __: None = Depends(require_legacy_booking_api),
):
    return crud.get_appointments(
        db,
        patient_id=patient_id,
        status=status_filter,
        from_datetime=from_,
        to_datetime=to,
        skip=skip,
        limit=limit,
    )


@app.get(
    "/appointments/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"]
)
def read_appointment(
    appointment_id: int,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    db_appointment = crud.get_appointment(db, appointment_id)
    if db_appointment is None:
        raise not_found("Appointment")
    return db_appointment


@app.put(
    "/appointments/{appointment_id}", response_model=schemas.Appointment, tags=["appointments"]
)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentUpdate,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    db_appointment = crud.update_appointment(db, appointment_id, appointment)
    if db_appointment is None:
        raise not_found("Appointment")
    return db_appointment


@app.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["appointments"],
)
def delete_appointment(
    appointment_id: int,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    if crud.delete_appointment(db, appointment_id) is None:
        raise not_found("Appointment")
    return None


@app.get(
    "/patients/{patient_id}/appointments",
    response_model=list[schemas.Appointment],
    tags=["appointments"],
)
def read_patient_appointments(
    patient_id: int,
    db: DbSession,
    _: StaffUser,
    __: None = Depends(require_legacy_booking_api),
):
    if crud.get_patient(db, patient_id) is None:
        raise not_found("Patient")
    return crud.get_patient_appointments(db, patient_id)
