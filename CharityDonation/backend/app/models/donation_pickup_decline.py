import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class DonationPickupDecline(Base):
    __tablename__ = "donation_pickup_declines"
    __table_args__ = (
        UniqueConstraint(
            "donation_id",
            "volunteer_id",
            name="uq_donation_pickup_declines_donation_volunteer",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("donations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    volunteer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    declined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donation: Mapped["Donation"] = relationship("Donation", back_populates="pickup_declines")
