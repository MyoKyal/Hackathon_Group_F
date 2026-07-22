"""receiver photo confirmation with advisory AI verification

Revision ID: 006_receiver_photo
Revises: 005_warehouse_routing
Create Date: 2026-07-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_receiver_photo"
down_revision: Union[str, None] = "005_warehouse_routing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("deliveries", sa.Column("receiver_photo_path", sa.String(length=500), nullable=True))
    op.add_column("deliveries", sa.Column("photo_match", sa.Boolean(), nullable=True))
    op.add_column("deliveries", sa.Column("photo_verification_reasoning", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("deliveries", "photo_verification_reasoning")
    op.drop_column("deliveries", "photo_match")
    op.drop_column("deliveries", "receiver_photo_path")
