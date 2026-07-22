from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ItemCategory


class WarehouseSummary(BaseModel):
    id: UUID
    name: str
    lat: float
    lng: float


class InventoryItemResponse(BaseModel):
    warehouse_id: UUID
    warehouse_name: str
    category: ItemCategory
    quantity: int
