"""url_rip — RipJob table + LiveSet.source_external_id

Revision ID: 0009_url_rip
Revises: 0008_engagement
Create Date: 2026-05-27 00:00:01
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_url_rip"
down_revision = "0008_engagement"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # LiveSet.source_external_id — idempotency anchor for URL rips.
    # Distinct from source_url because the same platform video can have
    # many URL forms (youtube.com/watch?v=, youtu.be/, with/without &t=, etc.).
    op.add_column(
        "live_sets",
        sa.Column("source_external_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_live_sets_source_external_id",
        "live_sets",
        ["source_external_id"],
        postgresql_where=sa.text("source_external_id IS NOT NULL"),
    )

    # rip_jobs — per-URL ingest state visible in the Jobs drawer.
    op.create_table(
        "rip_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=True),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_url", sa.Text, nullable=False),
        sa.Column("source_external_id", sa.String(length=255), nullable=True),
        sa.Column("source_platform", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("progress_pct", sa.Integer, nullable=False, server_default="0"),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("error_text", sa.Text, nullable=True),
        sa.Column("probed_metadata", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("ytdlp_version", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_rip_jobs_submitted_by_created",
        "rip_jobs",
        ["submitted_by", sa.text("created_at desc")],
    )
    op.execute(
        "CREATE INDEX ix_rip_jobs_active ON rip_jobs (status) "
        "WHERE status NOT IN ('ready', 'failed')"
    )
    op.execute(
        "CREATE INDEX ix_rip_jobs_external_id ON rip_jobs "
        "(source_platform, source_external_id) "
        "WHERE source_external_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_rip_jobs_external_id")
    op.execute("DROP INDEX IF EXISTS ix_rip_jobs_active")
    op.drop_table("rip_jobs")
    op.drop_index("ix_live_sets_source_external_id", table_name="live_sets")
    op.drop_column("live_sets", "source_external_id")
