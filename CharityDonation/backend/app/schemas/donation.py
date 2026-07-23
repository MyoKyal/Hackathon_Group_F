from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.delivery import DeliveryStatus
from app.models.donation import DonationStatus
from app.models.enums import ItemCategory
from app.schemas.common import Location
from app.schemas.delivery import DeliverySummary
from app.schemas.volunteer import VolunteerInfo
from app.schemas.warehouse import WarehouseSummary


class DonationCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    item_category: ItemCategory
    description: str | None = None
    quantity: int = Field(1, gt=0)
    weight_kg: float = Field(1, gt=0)
    pickup_location: Location
    target_receiver_id: UUID | None = None


class DonationResponse(BaseModel):
    id: UUID
    donor_id: UUID
    item_name: str
    item_category: ItemCategory
    description: str | None
    quantity: int
    weight_kg: float
    pickup_lat: float
    pickup_lng: float
    target_receiver_id: UUID | None
    status: DonationStatus
    warehouse: WarehouseSummary
    pickup_status: DeliveryStatus
    pickup_volunteer_id: UUID | None
    pickup_volunteer: VolunteerInfo | None = None
    pickup_stage1_score: float | None
    pickup_gemini_reasoning: str | None
    pickup_volunteer_confirmed: bool
    pickup_completed_at: datetime | None
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
    quantity_needed: int
    distance_km: float
    score: float


class DonationBrowseItem(DonationResponse):
    donor_name: str
