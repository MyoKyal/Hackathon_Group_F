import enum
import uuid
from datetime import datetime, time

from geoalchemy2 import Geography
from sqlalchemy import ARRAY, Boolean, DateTime, Enum, Float, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class VolunteerStatus(str, enum.Enum):
    none = "none"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class TransportationType(str, enum.Enum):
    walking = "walking"
    bicycle = "bicycle"
    motorbike = "motorbike"
    car = "car"
    truck = "truck"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    base_location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True
    )
    is_volunteer: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    volunteer_status: Mapped[VolunteerStatus] = mapped_column(
        Enum(VolunteerStatus, name="volunteer_status_enum", native_enum=True),
        nullable=False,
        server_default=VolunteerStatus.none.value,
    )
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    transportation_type: Mapped[TransportationType | None] = mapped_column(
        Enum(TransportationType, name="transportation_type_enum", native_enum=True),
        nullable=True,
    )
    max_carrying_capacity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_travel_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    township: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_days: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    available_start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    available_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    preferred_categories: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    completed_deliveries: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    active_deliveries: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    reliability_rating: Mapped[float] = mapped_column(Float, nullable=False, server_default="5.0")
    avg_delivery_time_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donations: Mapped[list["Donation"]] = relationship(
        "Donation",
        back_populates="donor",
        foreign_keys="Donation.donor_id",
    )
    receiver_requests: Mapped[list["ReceiverRequest"]] = relationship(
        "ReceiverRequest",
        back_populates="requester",
    )
