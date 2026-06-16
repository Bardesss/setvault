"""7c monitors — monitor + monitor_discovery tables, per-source rate limits,
monitor system-config columns

Revision ID: 0017_7c_monitors
Revises: 0016_7a_ingest_source_state
Create Date: 2026-06-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0017_7c_monitors"
down_revision = "0016_7a_ingest_source_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monitor",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("query_text", sa.String(length=255), nullable=True),
        sa.Column("source_kind", sa.String(length=32), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("per_poll_cap", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE",
                                name="fk_monitor_owner_user_id_users"),
    )
    op.create_table(
        "monitor_discovery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("monitor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_kind", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("uploader", sa.String(length=255), nullable=True),
        sa.Column("webpage_url", sa.Text(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("url_rip_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["monitor_id"], ["monitor.id"], ondelete="CASCADE",
                                name="fk_monitor_discovery_monitor_id_monitor"),
        sa.ForeignKeyConstraint(["url_rip_id"], ["rip_jobs.id"], ondelete="SET NULL",
                                name="fk_monitor_discovery_url_rip_id_rip_jobs"),
        sa.UniqueConstraint("monitor_id", "source_kind", "external_id",
                            name="uq_monitor_discovery_monitor_source_ext"),
    )
    op.add_column("ingest_source_state",
        sa.Column("rate_limit_max", sa.Integer(), nullable=False, server_default="30"))
    op.add_column("ingest_source_state",
        sa.Column("rate_limit_window_seconds", sa.Integer(), nullable=False,
                  server_default="60"))
    op.add_column("system_config",
        sa.Column("monitors_allow_all_users", sa.Boolean(), nullable=False,
                  server_default=sa.false()))
    op.add_column("system_config",
        sa.Column("monitor_interval_seconds", sa.Integer(), nullable=False,
                  server_default="3600"))


def downgrade() -> None:
    op.drop_column("system_config", "monitor_interval_seconds")
    op.drop_column("system_config", "monitors_allow_all_users")
    op.drop_column("ingest_source_state", "rate_limit_window_seconds")
    op.drop_column("ingest_source_state", "rate_limit_max")
    op.drop_table("monitor_discovery")
    op.drop_table("monitor")
