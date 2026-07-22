from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.donation import DonationStatus
from app.schemas.common import Location
from app.schemas.delivery import DeliverySummary


class DonationCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    item_category: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    quantity: int = Field(1, gt=0)
    pickup_location: Location
    target_receiver_id: UUID | None = None


class DonationResponse(BaseModel):
    id: UUID
    donor_id: UUID
    item_name: str
    item_category: str
    description: str | None
    quantity: int
    pickup_lat: float
    pickup_lng: float
    target_receiver_id: UUID | None
    status: DonationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class DonationDetailResponse(DonationResponse):
    delivery: DeliverySummary | None = None


class DonationCreateResponse(DonationResponse):
    delivery: DeliverySummary | None = None


class MatchPreviewItem(BaseModel):
    request_id: UUID
    requester_name: str
    item_name: str
    distance_km: float
    score: float
