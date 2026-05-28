"""5c-webhooks — library_webhooks for §J15 library refresh hooks

Each row: name, target URL, event filter (jsonb array of audit-action
strings — e.g. ``["set.published", "set.updated", "set.purged"]``), optional
body template (jsonb; if null the dispatcher posts a default
``{"event", "set_slug", "set_id", "title"}`` shape), enabled flag, plus
last-call telemetry.

Revision ID: 0014_5c_webhooks
Revises: 0013_5b
Create Date: 2026-05-28 14:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014_5c_webhooks"
down_revision = "0013_5b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "library_webhooks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("target_url", sa.String(length=2048), nullable=False),
        sa.Column(
            "events", postgresql.JSONB, nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("body_template", postgresql.JSONB, nullable=True),
        sa.Column(
            "headers", postgresql.JSONB, nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "enabled", sa.Boolean, nullable=False, server_default=sa.text("true"),
        ),
        sa.Column("last_call_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status_code", sa.Integer, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.execute(
        "CREATE INDEX ix_library_webhooks_enabled ON library_webhooks (enabled) "
        "WHERE enabled = true"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_library_webhooks_enabled")
    op.drop_table("library_webhooks")
