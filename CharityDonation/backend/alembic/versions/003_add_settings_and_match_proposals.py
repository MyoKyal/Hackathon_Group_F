"""add app_settings and match_proposals

Revision ID: 003_settings_match_proposals
Revises: 002_add_is_admin
Create Date: 2026-07-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_settings_match_proposals"
down_revision: Union[str, None] = "002_add_is_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

match_proposal_status_enum = postgresql.ENUM(
    "pending", "approved", "rejected", name="match_proposal_status_enum", create_type=False
)


def upgrade() -> None:
    match_proposal_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "require_match_approval", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT INTO app_settings (require_match_approval) VALUES (false)")

    op.create_table(
        "match_proposals",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("donation_id", sa.UUID(), nullable=False),
        sa.Column("receiver_request_id", sa.UUID(), nullable=True),
        sa.Column("receiver_id", sa.UUID(), nullable=False),
        sa.Column("stage1_score", sa.Float(), nullable=True),
        sa.Column("gemini_reasoning", sa.Text(), nullable=True),
        sa.Column(
            "status",
            match_proposal_status_enum,
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["donation_id"], ["donations.id"]),
        sa.ForeignKeyConstraint(["receiver_request_id"], ["receiver_requests.id"]),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"]),
    )
    op.create_index("ix_match_proposals_donation_id", "match_proposals", ["donation_id"])
    op.create_index("ix_match_proposals_receiver_id", "match_proposals", ["receiver_id"])
    op.create_index("ix_match_proposals_status", "match_proposals", ["status"])


def downgrade() -> None:
    op.drop_index("ix_match_proposals_status", table_name="match_proposals")
    op.drop_index("ix_match_proposals_receiver_id", table_name="match_proposals")
    op.drop_index("ix_match_proposals_donation_id", table_name="match_proposals")
    op.drop_table("match_proposals")
    op.drop_table("app_settings")
    match_proposal_status_enum.drop(op.get_bind(), checkfirst=True)
