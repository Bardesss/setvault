# infra/migrations/versions/0019_catalog_merge_columns.py
"""catalog merge columns — reversible-merge tombstones on the 4 entity tables

Revision ID: 0019_catalog_merge_columns
Revises: 0018_single_user_auto_login
Create Date: 2026-06-17 13:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0019_catalog_merge_columns"
down_revision = "0018_single_user_auto_login"
branch_labels = None
depends_on = None

_TABLES = ("artists", "venues", "parties", "series")


def upgrade() -> None:
    for t in _TABLES:
        op.add_column(t, sa.Column("merged_into_id", UUID(as_uuid=True),
                                   sa.ForeignKey(f"{t}.id", ondelete="SET NULL"), nullable=True))
        op.add_column(t, sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True))
        op.add_column(t, sa.Column("merge_manifest", JSONB, nullable=True))
        op.create_index(f"ix_{t}_merged_into_id", t, ["merged_into_id"])


def downgrade() -> None:
    for t in _TABLES:
        op.drop_index(f"ix_{t}_merged_into_id", table_name=t)
        op.drop_column(t, "merge_manifest")
        op.drop_column(t, "merged_at")
        op.drop_column(t, "merged_into_id")
