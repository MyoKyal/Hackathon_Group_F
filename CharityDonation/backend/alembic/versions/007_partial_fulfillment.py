"""add quantity_fulfilled to receiver_requests

Revision ID: 007_partial_fulfillment
Revises: 006_receiver_photo
Create Date: 2026-07-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_partial_fulfillment"
down_revision: Union[str, None] = "006_receiver_photo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "receiver_requests",
        sa.Column("quantity_fulfilled", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("receiver_requests", "quantity_fulfilled")
