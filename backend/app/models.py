"""SQLAlchemy models.

Changes from the original scaffold:
  - `date_of_birth` is a real `Date`, not a `String` that happened to look
    like a date. ISO strings were never validated at the database level.
  - `Appointment.patient_id` is an actual foreign key with `ON DELETE CASCADE`.
    It was a bare integer, so appointments could point at patients that no
    longer existed.
  - `status` columns are `Enum`s, so an invalid value fails at the database
    boundary instead of silently storing "confimed".
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingStatus(str, enum.Enum):
    """Lifecycle of a public booking request.

    Distinct from `AppointmentStatus`: a booking is a request off the website
    that has not necessarily been turned into a scheduled appointment yet.
    """

    NEW = "new"
    CONTACTED = "contacted"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Nullable because a patient arriving through the public booking form gives
    # a phone number, not an email address. Phone is the reliable identifier
    # here; email is a bonus. A unique index tolerates many NULLs on both
    # SQLite and PostgreSQL, so this does not force placeholder addresses.
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    # Also unique, and the primary dedupe key. Indian mobiles are 10 digits;
    # stored as given so the clinic can recognise a number at a glance.
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class User(Base):
    """Clinic staff. Never exposed to unauthenticated callers."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Booking(Base):
    """A public booking request, exactly the fields the website form collects.

    Deliberately separate from `Patient`: the form asks for name, phone, date
    and concern, and inventing a Patient row for a half-filled web form would
    put incomplete records into the clinical record.
    """

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # Optional on purpose. The booking form is a two-field form; demanding an
    # email is the single biggest reason health booking forms get abandoned.
    # It is carried through to the Patient record when staff supply one.
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    preferred_date: Mapped[date] = mapped_column(Date, nullable=False)
    concern: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, native_enum=False, length=20),
        default=BookingStatus.NEW,
        server_default=BookingStatus.NEW.value,
        nullable=False,
        index=True,
    )
    # Set once staff confirm a real slot and create the Appointment.
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Naive local time on purpose. A single consultant in a single timezone
    # means an appointment is a wall-clock moment, not an instant, and storing
    # it without an offset removes a whole class of "the 6pm call moved to 1pm
    # after the DST change" bugs. Overlap checks below compare naive values.
    appointment_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, server_default="30")
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False, length=20),
        default=AppointmentStatus.PENDING,
        server_default=AppointmentStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    doctor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
