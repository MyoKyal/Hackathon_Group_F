from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.models.delivery import DeliveryStatus
from app.models.enums import ItemCategory
from app.schemas.warehouse import WarehouseSummary


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
    receiver_photo_path: str | None = None
    photo_match: bool | None = None
    photo_verification_reasoning: str | None = None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class DonationSummary(BaseModel):
    id: UUID
    item_name: str
    item_category: ItemCategory
    quantity: int
    pickup_lat: float
    pickup_lng: float


class ReceiverSummary(BaseModel):
    id: UUID
    full_name: str


class AssignmentResponse(BaseModel):
    id: UUID
    leg: Literal["pickup", "delivery"]
    status: DeliveryStatus
    volunteer_id: UUID | None
    is_current_offer: bool
    donation: DonationSummary
    receiver: ReceiverSummary | None = None
    warehouse: WarehouseSummary | None = None
    stage1_score: float | None
    gemini_reasoning: str | None
    volunteer_confirmed: bool
    receiver_confirmed: bool | None = None
    created_at: datetime


class DeliveryDetailResponse(DeliverySummary):
    donation: DonationSummary
    receiver: ReceiverSummary


class MatchCardResponse(BaseModel):
    id: UUID
    status: DeliveryStatus
    created_at: datetime
    stage1_score: float | None
    gemini_reasoning: str | None
    donation_item_name: str
    donation_quantity: int
    donor_name: str
    request_item_name: str | None
    request_quantity_needed: int | None
    receiver_name: str
