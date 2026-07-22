from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.delivery import DeliveryStatus


class DeliverySummary(BaseModel):
    id: UUID
    donation_id: UUID
    receiver_request_id: UUID | None
    receiver_id: UUID
    volunteer_id: UUID | None
    stage1_score: float | None
    gemini_reasoning: str | None
    status: DeliveryStatus
    volunteer_confirmed: bool
    receiver_confirmed: bool
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class DonationSummary(BaseModel):
    id: UUID
    item_name: str
    item_category: str
    quantity: int
    pickup_lat: float
    pickup_lng: float


class ReceiverSummary(BaseModel):
    id: UUID
    full_name: str


class AssignmentResponse(BaseModel):
    id: UUID
    status: DeliveryStatus
    volunteer_id: UUID | None
    is_current_offer: bool
    donation: DonationSummary
    receiver: ReceiverSummary
    stage1_score: float | None
    gemini_reasoning: str | None
    volunteer_confirmed: bool
    receiver_confirmed: bool
    created_at: datetime


class DeliveryDetailResponse(DeliverySummary):
    donation: DonationSummary
    receiver: ReceiverSummary
