import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.delivery import DeliveryStatus
from app.models.enums import ItemCategory


class DonationStatus(str, enum.Enum):
    pending = "pending"
    matched = "matched"
    in_transit = "in_transit"
    completed = "completed"


class Donation(Base):
    __tablename__ = "donations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_donations_quantity_positive"),
        CheckConstraint("weight_kg > 0", name="ck_donations_weight_kg_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    donor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_category: Mapped[ItemCategory] = mapped_column(
        Enum(ItemCategory, name="item_category_enum", native_enum=True),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False, server_default="1")
    pickup_location: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    target_receiver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[DonationStatus] = mapped_column(
        Enum(DonationStatus, name="donation_status_enum", native_enum=True),
        nullable=False,
        server_default=DonationStatus.pending.value,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True
    )
    pickup_volunteer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    pickup_status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status_enum", native_enum=True),
        nullable=False,
        server_default=DeliveryStatus.awaiting_volunteer.value,
        index=True,
    )
    pickup_stage1_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pickup_gemini_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    pickup_volunteer_confirmed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    pickup_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donor: Mapped["User"] = relationship(
        "User",
        back_populates="donations",
        foreign_keys=[donor_id],
    )
    delivery: Mapped["Delivery | None"] = relationship(
        "Delivery",
        back_populates="donation",
        uselist=False,
    )
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    pickup_declines: Mapped[list["DonationPickupDecline"]] = relationship(
        "DonationPickupDecline", back_populates="donation"
    )
