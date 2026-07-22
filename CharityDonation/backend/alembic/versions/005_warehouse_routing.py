"""warehouse routing: item category enum, warehouses, two-leg pickup

Revision ID: 005_warehouse_routing
Revises: 004_volunteer_profile
Create Date: 2026-07-23

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_warehouse_routing"
down_revision: Union[str, None] = "004_volunteer_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

item_category_enum = postgresql.ENUM(
    "food", "clothes", "water", "medicine", "stationary",
    name="item_category_enum", create_type=False,
)
# Already created in 001 — reused here for the new pickup_status column, NOT re-created.
delivery_status_enum = postgresql.ENUM(
    "awaiting_volunteer", "in_transit", "completed", "cancelled",
    name="delivery_status_enum", create_type=False,
)


def upgrade() -> None:
    item_category_enum.create(op.get_bind(), checkfirst=True)

    # 1. Reset test data invalidated by the new category enum / new donation columns.
    op.execute(
        "TRUNCATE TABLE match_proposals, volunteer_declines, deliveries, "
        "donations, receiver_requests CASCADE"
    )

    # 2. Convert free-text category columns to the enum (tables now empty).
    op.execute(
        "ALTER TABLE donations ALTER COLUMN item_category TYPE item_category_enum "
        "USING item_category::item_category_enum"
    )
    op.execute(
        "ALTER TABLE receiver_requests ALTER COLUMN item_category TYPE item_category_enum "
        "USING item_category::item_category_enum"
    )
    op.create_index(op.f("ix_donations_item_category"), "donations", ["item_category"])
    op.create_index(
        op.f("ix_receiver_requests_item_category"), "receiver_requests", ["item_category"]
    )

    # 3. Warehouses + inventory.
    op.create_table(
        "warehouses",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.execute("CREATE INDEX ix_warehouses_location ON warehouses USING GIST (location)")

    op.create_table(
        "warehouse_inventory",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("category", item_category_enum, nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint("quantity >= 0", name="ck_warehouse_inventory_quantity_nonnegative"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "warehouse_id", "category", name="uq_warehouse_inventory_warehouse_category"
        ),
    )
    op.create_index(
        op.f("ix_warehouse_inventory_warehouse_id"), "warehouse_inventory", ["warehouse_id"]
    )

    # 4. Seed the two fixed warehouses + one zeroed inventory row per category.
    #    Coordinates given as (lat, lng); ST_MakePoint takes (lng, lat).
    op.execute(
        """
        INSERT INTO warehouses (id, name, location) VALUES
        (gen_random_uuid(), 'Yangon',
            ST_SetSRID(ST_MakePoint(95.8518993, 16.8388795), 4326)::geography),
        (gen_random_uuid(), 'Mandalay',
            ST_SetSRID(ST_MakePoint(95.9934217, 21.9403394), 4326)::geography)
        """
    )
    op.execute(
        """
        INSERT INTO warehouse_inventory (id, warehouse_id, category, quantity)
        SELECT gen_random_uuid(), w.id, c.category, 0
        FROM warehouses w
        CROSS JOIN (
            SELECT unnest(enum_range(NULL::item_category_enum)) AS category
        ) c
        """
    )

    # 5. Leg-1 (pickup) columns on donations.
    op.add_column("donations", sa.Column("warehouse_id", sa.UUID(), nullable=False))
    op.add_column("donations", sa.Column("pickup_volunteer_id", sa.UUID(), nullable=True))
    op.add_column(
        "donations",
        sa.Column(
            "pickup_status",
            delivery_status_enum,
            server_default=sa.text("'awaiting_volunteer'"),
            nullable=False,
        ),
    )
    op.add_column("donations", sa.Column("pickup_stage1_score", sa.Float(), nullable=True))
    op.add_column("donations", sa.Column("pickup_gemini_reasoning", sa.Text(), nullable=True))
    op.add_column(
        "donations",
        sa.Column(
            "pickup_volunteer_confirmed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column("donations", sa.Column("pickup_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_donations_warehouse_id", "donations", "warehouses", ["warehouse_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_donations_pickup_volunteer_id", "donations", "users", ["pickup_volunteer_id"], ["id"]
    )
    op.create_index(op.f("ix_donations_warehouse_id"), "donations", ["warehouse_id"])
    op.create_index(op.f("ix_donations_pickup_volunteer_id"), "donations", ["pickup_volunteer_id"])
    op.create_index(op.f("ix_donations_pickup_status"), "donations", ["pickup_status"])

    # 6. Leg-1 decline table (mirrors volunteer_declines).
    op.create_table(
        "donation_pickup_declines",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("donation_id", sa.UUID(), nullable=False),
        sa.Column("volunteer_id", sa.UUID(), nullable=False),
        sa.Column(
            "declined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["donation_id"], ["donations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volunteer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "donation_id", "volunteer_id", name="uq_donation_pickup_declines_donation_volunteer"
        ),
    )
    op.create_index(
        op.f("ix_donation_pickup_declines_donation_id"),
        "donation_pickup_declines",
        ["donation_id"],
    )
    op.create_index(
        op.f("ix_donation_pickup_declines_volunteer_id"),
        "donation_pickup_declines",
        ["volunteer_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_donation_pickup_declines_volunteer_id"), table_name="donation_pickup_declines"
    )
    op.drop_index(
        op.f("ix_donation_pickup_declines_donation_id"), table_name="donation_pickup_declines"
    )
    op.drop_table("donation_pickup_declines")

    op.drop_index(op.f("ix_donations_pickup_status"), table_name="donations")
    op.drop_index(op.f("ix_donations_pickup_volunteer_id"), table_name="donations")
    op.drop_index(op.f("ix_donations_warehouse_id"), table_name="donations")
    op.drop_constraint("fk_donations_pickup_volunteer_id", "donations", type_="foreignkey")
    op.drop_constraint("fk_donations_warehouse_id", "donations", type_="foreignkey")
    op.drop_column("donations", "pickup_completed_at")
    op.drop_column("donations", "pickup_volunteer_confirmed")
    op.drop_column("donations", "pickup_gemini_reasoning")
    op.drop_column("donations", "pickup_stage1_score")
    op.drop_column("donations", "pickup_status")
    op.drop_column("donations", "pickup_volunteer_id")
    op.drop_column("donations", "warehouse_id")

    op.drop_index(op.f("ix_warehouse_inventory_warehouse_id"), table_name="warehouse_inventory")
    op.drop_table("warehouse_inventory")
    op.execute("DROP INDEX IF EXISTS ix_warehouses_location")
    op.drop_table("warehouses")

    op.drop_index(op.f("ix_receiver_requests_item_category"), table_name="receiver_requests")
    op.drop_index(op.f("ix_donations_item_category"), table_name="donations")
    op.execute(
        "ALTER TABLE receiver_requests ALTER COLUMN item_category TYPE varchar(64) "
        "USING item_category::text"
    )
    op.execute(
        "ALTER TABLE donations ALTER COLUMN item_category TYPE varchar(64) "
        "USING item_category::text"
    )

    item_category_enum.drop(op.get_bind(), checkfirst=True)
