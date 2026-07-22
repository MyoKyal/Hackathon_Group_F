from datetime import time
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import TransportationType, VolunteerStatus


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=32)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    is_volunteer: bool
    volunteer_status: VolunteerStatus
    is_available: bool
    is_admin: bool

    transportation_type: TransportationType | None = None
    max_carrying_capacity_kg: float | None = None
    max_travel_distance_km: float | None = None
    township: str | None = None
    full_address: str | None = None
    available_days: list[str] | None = None
    available_start_time: time | None = None
    available_end_time: time | None = None
    preferred_categories: list[str] | None = None

    completed_deliveries: int = 0
    active_deliveries: int = 0
    reliability_rating: float = 5.0
    avg_delivery_time_minutes: float | None = None

    model_config = {"from_attributes": True}


class SignupResponse(UserResponse):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
