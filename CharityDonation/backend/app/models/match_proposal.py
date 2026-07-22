import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class MatchProposalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MatchProposal(Base):
    __tablename__ = "match_proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    donation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("donations.id"), nullable=False, index=True
    )
    receiver_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("receiver_requests.id"), nullable=True
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    stage1_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gemini_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MatchProposalStatus] = mapped_column(
        Enum(MatchProposalStatus, name="match_proposal_status_enum", native_enum=True),
        nullable=False,
        server_default=MatchProposalStatus.pending.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donation: Mapped["Donation"] = relationship("Donation")
    receiver_request: Mapped["ReceiverRequest | None"] = relationship("ReceiverRequest")
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id])
