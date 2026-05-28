"""5d-playback-rate — user_set_state.playback_rate (Phase 5D player polish)

Persists per-user-per-set playback speed so the §E4 control sticks across
sessions. Default 1.0 matches normal-rate playback.

Revision ID: 0015_5d_playback_rate
Revises: 0014_5c_webhooks
Create Date: 2026-05-28 15:00:00
"""
import sqlalchemy as sa
from alembic import op

revision = "0015_5d_playback_rate"
down_revision = "0014_5c_webhooks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_set_state",
        sa.Column(
            "playback_rate", sa.Float, nullable=False,
            server_default=sa.text("1.0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("user_set_state", "playback_rate")
