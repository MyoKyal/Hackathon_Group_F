from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse, WarehouseInventory
from app.schemas.warehouse import InventoryItemResponse


def list_inventory(db: Session) -> list[InventoryItemResponse]:
    rows = db.execute(
        select(
            Warehouse.id,
            Warehouse.name,
            WarehouseInventory.category,
            WarehouseInventory.quantity,
        )
        .join(WarehouseInventory, WarehouseInventory.warehouse_id == Warehouse.id)
        .order_by(Warehouse.name, WarehouseInventory.category)
    ).all()
    return [
        InventoryItemResponse(
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name,
            category=category,
            quantity=quantity,
        )
        for warehouse_id, warehouse_name, category, quantity in rows
    ]
