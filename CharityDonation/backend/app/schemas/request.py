from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ItemCategory
from app.models.receiver_request import RequestStatus
from app.schemas.common import Location


class RequestCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    item_category: ItemCategory
    description: str | None = None
    quantity_needed: int = Field(1, gt=0)
    location: Location


class RequestUpdate(BaseModel):
    description: str | None = None
    quantity_needed: int | None = Field(None, gt=0)
    status: RequestStatus | None = None


class RequestResponse(BaseModel):
    id: UUID
    requester_id: UUID
    item_name: str
    item_category: ItemCategory
    description: str | None
    quantity_needed: int
    lat: float
    lng: float
    status: RequestStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class RequestBrowseItem(RequestResponse):
    requester_name: str
