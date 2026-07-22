from pydantic import BaseModel

from app.models.user import VolunteerStatus
from app.schemas.auth import UserResponse


class VolunteerApplyResponse(BaseModel):
    volunteer_status: VolunteerStatus


class VolunteerApproveResponse(UserResponse):
    pass
