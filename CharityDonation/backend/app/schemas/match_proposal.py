from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.match_proposal import MatchProposalStatus
from app.schemas.delivery import DonationSummary, ReceiverSummary


class MatchProposalResponse(BaseModel):
    id: UUID
    donation_id: UUID
    receiver_request_id: UUID | None
    receiver_id: UUID
    stage1_score: float | None
    gemini_reasoning: str | None
    status: MatchProposalStatus
    created_at: datetime
    donation: DonationSummary
    receiver: ReceiverSummary

    model_config = {"from_attributes": True}
