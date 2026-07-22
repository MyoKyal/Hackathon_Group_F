from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import VolunteerStatus


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

    model_config = {"from_attributes": True}


class SignupResponse(UserResponse):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
