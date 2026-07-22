"""add volunteer profile fields and donation weight

Revision ID: 004_volunteer_profile
Revises: 003_settings_match_proposals
Create Date: 2026-07-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_volunteer_profile"
down_revision: Union[str, None] = "003_settings_match_proposals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transportation_type_enum = postgresql.ENUM(
    "walking", "bicycle", "motorbike", "car", "truck",
    name="transportation_type_enum", create_type=False,
)


def upgrade() -> None:
    transportation_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("transportation_type", transportation_type_enum, nullable=True))
    op.add_column("users", sa.Column("max_carrying_capacity_kg", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("max_travel_distance_km", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("township", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("full_address", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("available_days", postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column("users", sa.Column("available_start_time", sa.Time(), nullable=True))
    op.add_column("users", sa.Column("available_end_time", sa.Time(), nullable=True))
    op.add_column("users", sa.Column("preferred_categories", postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column(
        "users",
        sa.Column("completed_deliveries", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("active_deliveries", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("reliability_rating", sa.Float(), server_default=sa.text("5.0"), nullable=False),
    )
    op.add_column("users", sa.Column("avg_delivery_time_minutes", sa.Float(), nullable=True))

    op.add_column(
        "donations",
        sa.Column("weight_kg", sa.Float(), server_default=sa.text("1"), nullable=False),
    )
    op.create_check_constraint(
        "ck_donations_weight_kg_positive", "donations", "weight_kg > 0"
    )


def downgrade() -> None:
    op.drop_constraint("ck_donations_weight_kg_positive", "donations", type_="check")
    op.drop_column("donations", "weight_kg")

    op.drop_column("users", "avg_delivery_time_minutes")
    op.drop_column("users", "reliability_rating")
    op.drop_column("users", "active_deliveries")
    op.drop_column("users", "completed_deliveries")
    op.drop_column("users", "preferred_categories")
    op.drop_column("users", "available_end_time")
    op.drop_column("users", "available_start_time")
    op.drop_column("users", "available_days")
    op.drop_column("users", "full_address")
    op.drop_column("users", "township")
    op.drop_column("users", "max_travel_distance_km")
    op.drop_column("users", "max_carrying_capacity_kg")
    op.drop_column("users", "transportation_type")

    transportation_type_enum.drop(op.get_bind(), checkfirst=True)
