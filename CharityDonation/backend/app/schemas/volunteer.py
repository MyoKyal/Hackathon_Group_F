from datetime import time

from pydantic import BaseModel, Field

from app.models.user import TransportationType, VolunteerStatus
from app.schemas.auth import UserResponse
from app.schemas.common import Location


class VolunteerApplyRequest(BaseModel):
    location: Location
    transportation_type: TransportationType
    max_travel_distance_km: float = Field(..., gt=0)
    township: str = Field(..., min_length=1, max_length=255)
    full_address: str = Field(..., min_length=1)
    available_days: list[str] = Field(..., min_length=1)
    available_start_time: time
    available_end_time: time
    preferred_categories: list[str] = []


class VolunteerApplyResponse(BaseModel):
    volunteer_status: VolunteerStatus


class VolunteerApproveResponse(UserResponse):
    pass
