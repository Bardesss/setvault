"""5b — system_config singleton (Phase 5B backend backbone)

Stores app-wide runtime settings that don't fit other tables: the cached
latest GitHub release tag for the J16 banner, plus the J17 audit retention
window. One row only — enforced by the ``CHECK (singleton)`` constraint.

Revision ID: 0013_5b
Revises: 0012_5a
Create Date: 2026-05-28 13:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013_5b"
down_revision = "0012_5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_config",
        sa.Column(
            "singleton", sa.Boolean, primary_key=True,
            server_default=sa.text("true"),
        ),
        sa.Column("latest_release_version", sa.String(length=40), nullable=True),
        sa.Column("latest_release_url", sa.String(length=2048), nullable=True),
        sa.Column("latest_release_etag", sa.String(length=255), nullable=True),
        sa.Column(
            "latest_release_checked_at", sa.DateTime(timezone=True), nullable=True,
        ),
        sa.Column(
            "audit_retention_days", sa.Integer, nullable=False,
            server_default=sa.text("90"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.CheckConstraint(
            "singleton = true",
            name="ck_system_config_singleton",
        ),
    )
    # Seed the singleton row so the GET path never has to handle a missing row.
    op.execute("INSERT INTO system_config (singleton) VALUES (true)")


def downgrade() -> None:
    op.drop_table("system_config")
