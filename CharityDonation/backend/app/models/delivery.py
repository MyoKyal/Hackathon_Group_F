import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class DeliveryStatus(str, enum.Enum):
    awaiting_volunteer = "awaiting_volunteer"
    in_transit = "in_transit"
    completed = "completed"
    cancelled = "cancelled"


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("donations.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    receiver_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("receiver_requests.id"), nullable=True
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    volunteer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    stage1_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gemini_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status_enum", native_enum=True),
        nullable=False,
        server_default=DeliveryStatus.awaiting_volunteer.value,
        index=True,
    )
    volunteer_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    receiver_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    donation: Mapped["Donation"] = relationship("Donation", back_populates="delivery")
    receiver_request: Mapped["ReceiverRequest | None"] = relationship(
        "ReceiverRequest", back_populates="deliveries"
    )
    declines: Mapped[list["VolunteerDecline"]] = relationship(
        "VolunteerDecline", back_populates="delivery"
    )
