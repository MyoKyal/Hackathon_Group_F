from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class RoutePoint(BaseModel):
    lat: float
    lng: float
    label: str


class RouteResponse(BaseModel):
    leg: Literal["pickup", "delivery"]
    volunteer_id: UUID | None
    volunteer_name: str | None
    waypoints: list[RoutePoint]
    geometry: list[list[float]] | None
    distance_km: float | None
    duration_min: float | None
    routed: bool
