import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ItemCategory


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    location: Mapped[object] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    inventory: Mapped[list["WarehouseInventory"]] = relationship(
        "WarehouseInventory", back_populates="warehouse"
    )


class WarehouseInventory(Base):
    __tablename__ = "warehouse_inventory"
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id", "category", name="uq_warehouse_inventory_warehouse_category"
        ),
        CheckConstraint("quantity >= 0", name="ck_warehouse_inventory_quantity_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[ItemCategory] = mapped_column(
        Enum(ItemCategory, name="item_category_enum", native_enum=True), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventory")
