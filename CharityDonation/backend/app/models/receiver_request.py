import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ItemCategory


class RequestStatus(str, enum.Enum):
    open = "open"
    matched = "matched"
    fulfilled = "fulfilled"


class ReceiverRequest(Base):
    __tablename__ = "receiver_requests"
    __table_args__ = (
        CheckConstraint("quantity_needed > 0", name="ck_receiver_requests_quantity_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_category: Mapped[ItemCategory] = mapped_column(
        Enum(ItemCategory, name="item_category_enum", native_enum=True),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity_needed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    location: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status_enum", native_enum=True),
        nullable=False,
        server_default=RequestStatus.open.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    requester: Mapped["User"] = relationship("User", back_populates="receiver_requests")
    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates="receiver_request")
