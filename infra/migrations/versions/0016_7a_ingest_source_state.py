"""ingest_source_state — per-source enable + health state machine

One row per source kind tracks whether that ingest source is enabled and its
health (healthy | degraded | auto_disabled | manually_disabled), plus the
consecutive-failure counter that drives auto-disable.

Revision ID: 0016_7a_ingest_source_state
Revises: 0015_5d_playback_rate
Create Date: 2026-06-15 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0016_7a_ingest_source_state"
down_revision = "0015_5d_playback_rate"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingest_source_state",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="healthy"),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint(
        "uq_ingest_source_state_kind", "ingest_source_state", ["kind"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_ingest_source_state_kind", "ingest_source_state", type_="unique"
    )
    op.drop_table("ingest_source_state")
