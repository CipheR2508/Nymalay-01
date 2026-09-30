"""Pydantic v2 request/response models.

Validation rules here are the server's contract. The frontend mirrors them for
fast feedback, but this layer is the one that actually holds - the two must stay
in sync with lib/../components/BookingForm.js and lib/api.js.
"""

from datetime import date, datetime, timedelta

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .models import AppointmentStatus, BookingStatus

PHONE_PATTERN = r"^\+?[0-9][0-9\s\-]{7,19}$"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _blank_to_none(value: str | None) -> str | None:
    """Treat whitespace-only strings as absent.

    An HTML form posts "" for every untouched text input; storing that as a
    name or an address is worse than storing NULL.
    """

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


# --------------------------------------------------------------------- patient


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    # Optional: patients who arrive through the public booking form give a
    # phone number, not an email address.
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20, pattern=PHONE_PATTERN)
    date_of_birth: date | None = None
    address: str | None = Field(None, max_length=1000)
    medical_history: str | None = Field(None, max_length=10_000)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = Field(None, max_length=20, pattern=PHONE_PATTERN)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def _required_names(cls, value):
        cleaned = _blank_to_none(value)
        if cleaned is None:
            raise ValueError("name is required")
        return cleaned

    @field_validator(
        "address", "medical_history", "emergency_contact_name", mode="before"
    )
    @classmethod
    def _optional_text(cls, value):
        return _blank_to_none(value)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20, pattern=PHONE_PATTERN)
    date_of_birth: date | None = None
    address: str | None = Field(None, max_length=1000)
    medical_history: str | None = Field(None, max_length=10_000)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = Field(None, max_length=20, pattern=PHONE_PATTERN)
    is_active: bool | None = None


class Patient(PatientBase, ORMModel):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


# ------------------------------------------------------------------------ user


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    full_name: str | None = Field(None, max_length=150)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    is_admin: bool = False


class User(UserBase, ORMModel):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime | None = None
    # Note: hashed_password is deliberately absent. It must never be serialised
    # out of this model, so it cannot leak through a forgotten response_model.


# ----------------------------------------------------------------------- token


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


# --------------------------------------------------------------------- booking


class BookingBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., max_length=20, pattern=PHONE_PATTERN)
    email: EmailStr | None = None
    preferred_date: date
    concern: str = Field(..., min_length=10, max_length=2000)

    @field_validator("name", "concern", mode="before")
    @classmethod
    def _strip(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def _optional_email(cls, value):
        return _blank_to_none(value)

    @field_validator("preferred_date")
    @classmethod
    def _not_in_the_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("preferred_date cannot be in the past")
        return value


class BookingCreate(BookingBase):
    pass


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class Booking(BookingBase, ORMModel):
    id: int
    status: BookingStatus
    patient_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None


# ----------------------------------------------------------------- appointment


class AppointmentBase(BaseModel):
    patient_id: int
    appointment_date: datetime
    duration_minutes: int = Field(30, ge=10, le=180)
    doctor_notes: str | None = Field(None, max_length=5000)


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    appointment_date: datetime | None = None
    duration_minutes: int | None = Field(None, ge=10, le=180)
    doctor_notes: str | None = Field(None, max_length=5000)
    status: AppointmentStatus | None = None


class Appointment(AppointmentBase, ORMModel):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime | None = None


# ------------------------------------------------------------------ scheduling


class ScheduleBookingRequest(BaseModel):
    """Turn a confirmed booking request into a real appointment.

    Everything needed to close the loop in one call, so the patient record, the
    appointment and the booking status can never end up half-written. Staff use
    this from the booking queue the moment they agree a slot with the patient.

    `appointment_date` is naive local wall-clock time; see the model comment.
    """

    appointment_date: datetime
    duration_minutes: int = Field(45, ge=10, le=180)

    # Patient details, so staff can complete the record while they have the
    # booking in front of them instead of opening a second form.
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    # Falls back to the address on the booking when omitted.
    email: EmailStr | None = None
    # Falls back to the booking's phone, which is always present.
    phone: str | None = Field(None, max_length=20, pattern=PHONE_PATTERN)
    date_of_birth: date | None = None
    doctor_notes: str | None = Field(None, max_length=5000)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def _required_names(cls, value):
        cleaned = _blank_to_none(value)
        if cleaned is None:
            raise ValueError("name is required")
        return cleaned

    @field_validator("doctor_notes", mode="before")
    @classmethod
    def _optional_notes(cls, value):
        return _blank_to_none(value)

    @field_validator("appointment_date")
    @classmethod
    def _must_be_future(cls, value: datetime) -> datetime:
        # A small grace period absorbs clock skew and staff confirming a slot
        # for "now" while the request is still open.
        if value < datetime.now() - timedelta(minutes=15):
            raise ValueError("appointment_date cannot be in the past")
        return value


class ScheduledBooking(BaseModel):
    """What `POST /bookings/{id}/schedule` returns.

    All three records, so the staff screen can show the confirmed slot and hand
    the patient a WhatsApp confirmation without a second round trip.
    """

    booking: Booking
    patient: Patient
    appointment: Appointment
    reused_patient: bool = Field(
        description=(
            "True when an existing patient record was matched by phone or email "
            "rather than a new one being created."
        )
    )
