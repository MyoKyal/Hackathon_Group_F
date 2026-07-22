from pydantic import BaseModel


class SettingsResponse(BaseModel):
    require_match_approval: bool

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    require_match_approval: bool
