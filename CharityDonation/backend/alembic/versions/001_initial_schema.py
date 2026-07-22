"""initial schema with postgis

Revision ID: 001_initial
Revises:
Create Date: 2026-07-22

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

volunteer_status_enum = postgresql.ENUM(
    "none", "pending", "approved", "rejected", name="volunteer_status_enum", create_type=False
)
donation_status_enum = postgresql.ENUM(
    "pending", "matched", "in_transit", "completed", name="donation_status_enum", create_type=False
)
request_status_enum = postgresql.ENUM(
    "open", "matched", "fulfilled", name="request_status_enum", create_type=False
)
delivery_status_enum = postgresql.ENUM(
    "awaiting_volunteer", "in_transit", "completed", "cancelled",
    name="delivery_status_enum", create_type=False,
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    volunteer_status_enum.create(op.get_bind(), checkfirst=True)
    donation_status_enum.create(op.get_bind(), checkfirst=True)
    request_status_enum.create(op.get_bind(), checkfirst=True)
    delivery_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column(
            "base_location",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=True,
        ),
        sa.Column("is_volunteer", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "volunteer_status",
            volunteer_status_enum,
            server_default=sa.text("'none'"),
            nullable=False,
        ),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.execute(
        "CREATE INDEX ix_users_base_location ON users USING GIST (base_location)"
    )

    op.create_table(
        "donations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("donor_id", sa.UUID(), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("item_category", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "pickup_location",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("target_receiver_id", sa.UUID(), nullable=True),
        sa.Column(
            "status",
            donation_status_enum,
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="ck_donations_quantity_positive"),
        sa.ForeignKeyConstraint(["donor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_receiver_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_donations_donor_id"), "donations", ["donor_id"], unique=False)
    op.create_index(op.f("ix_donations_status"), "donations", ["status"], unique=False)
    op.execute(
        "CREATE INDEX ix_donations_pickup_location ON donations USING GIST (pickup_location)"
    )

    op.create_table(
        "receiver_requests",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("requester_id", sa.UUID(), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("item_category", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity_needed", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            request_status_enum,
            server_default=sa.text("'open'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity_needed > 0", name="ck_receiver_requests_quantity_positive"),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_receiver_requests_requester_id"), "receiver_requests", ["requester_id"], unique=False
    )
    op.create_index(op.f("ix_receiver_requests_status"), "receiver_requests", ["status"], unique=False)
    op.execute(
        "CREATE INDEX ix_receiver_requests_location ON receiver_requests USING GIST (location)"
    )

    op.create_table(
        "deliveries",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("donation_id", sa.UUID(), nullable=False),
        sa.Column("receiver_request_id", sa.UUID(), nullable=True),
        sa.Column("receiver_id", sa.UUID(), nullable=False),
        sa.Column("volunteer_id", sa.UUID(), nullable=True),
        sa.Column("stage1_score", sa.Float(), nullable=True),
        sa.Column("gemini_reasoning", sa.Text(), nullable=True),
        sa.Column(
            "status",
            delivery_status_enum,
            server_default=sa.text("'awaiting_volunteer'"),
            nullable=False,
        ),
        sa.Column("volunteer_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("receiver_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["donation_id"], ["donations.id"]),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["receiver_request_id"], ["receiver_requests.id"]),
        sa.ForeignKeyConstraint(["volunteer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("donation_id"),
    )
    op.create_index(op.f("ix_deliveries_donation_id"), "deliveries", ["donation_id"], unique=True)
    op.create_index(op.f("ix_deliveries_receiver_id"), "deliveries", ["receiver_id"], unique=False)
    op.create_index(op.f("ix_deliveries_status"), "deliveries", ["status"], unique=False)
    op.create_index(op.f("ix_deliveries_volunteer_id"), "deliveries", ["volunteer_id"], unique=False)

    op.create_table(
        "volunteer_declines",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("delivery_id", sa.UUID(), nullable=False),
        sa.Column("volunteer_id", sa.UUID(), nullable=False),
        sa.Column(
            "declined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["delivery_id"], ["deliveries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volunteer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id", "volunteer_id", name="uq_volunteer_declines_delivery_volunteer"),
    )
    op.create_index(
        op.f("ix_volunteer_declines_delivery_id"), "volunteer_declines", ["delivery_id"], unique=False
    )
    op.create_index(
        op.f("ix_volunteer_declines_volunteer_id"), "volunteer_declines", ["volunteer_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_volunteer_declines_volunteer_id"), table_name="volunteer_declines")
    op.drop_index(op.f("ix_volunteer_declines_delivery_id"), table_name="volunteer_declines")
    op.drop_table("volunteer_declines")

    op.drop_index(op.f("ix_deliveries_volunteer_id"), table_name="deliveries")
    op.drop_index(op.f("ix_deliveries_status"), table_name="deliveries")
    op.drop_index(op.f("ix_deliveries_receiver_id"), table_name="deliveries")
    op.drop_index(op.f("ix_deliveries_donation_id"), table_name="deliveries")
    op.drop_table("deliveries")

    op.execute("DROP INDEX IF EXISTS ix_receiver_requests_location")
    op.drop_index(op.f("ix_receiver_requests_status"), table_name="receiver_requests")
    op.drop_index(op.f("ix_receiver_requests_requester_id"), table_name="receiver_requests")
    op.drop_table("receiver_requests")

    op.execute("DROP INDEX IF EXISTS ix_donations_pickup_location")
    op.drop_index(op.f("ix_donations_status"), table_name="donations")
    op.drop_index(op.f("ix_donations_donor_id"), table_name="donations")
    op.drop_table("donations")

    op.execute("DROP INDEX IF EXISTS ix_users_base_location")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    delivery_status_enum.drop(op.get_bind(), checkfirst=True)
    request_status_enum.drop(op.get_bind(), checkfirst=True)
    donation_status_enum.drop(op.get_bind(), checkfirst=True)
    volunteer_status_enum.drop(op.get_bind(), checkfirst=True)
