"""embed — live_sets.embed_allowed

Revision ID: 0011_embed
Revises: 0010_api_tokens
Create Date: 2026-05-27 00:00:03
"""
import sqlalchemy as sa
from alembic import op

revision = "0011_embed"
down_revision = "0010_api_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "live_sets",
        sa.Column("embed_allowed", sa.Boolean, nullable=False,
                  server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("live_sets", "embed_allowed")
