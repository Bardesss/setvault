"""providers + enrichment

Revision ID: 0007_providers
Revises: 0006_tracklist
Create Date: 2026-05-17 00:00:01
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_providers"
down_revision = "0006_tracklist"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "provider_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_kind", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("encrypted_config", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("field_priority", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "provider_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_kind", sa.String(32), nullable=False),
        sa.Column("query_key", sa.String(512), nullable=False),
        sa.Column("response", postgresql.JSONB, nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    # Composite index serves the orchestrator's (provider_kind, query_key)
    # cache lookup; the expires_at filter is applied as a cheap residual.
    # (A `WHERE expires_at > now()` partial index is not possible — Postgres
    # requires IMMUTABLE functions in index predicates and now() is STABLE.)
    op.create_index("ix_provider_responses_lookup",
                    "provider_responses", ["provider_kind", "query_key"])

    op.create_table(
        "resolve_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="queued"),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("resolve_jobs")
    op.drop_table("provider_responses")
    op.drop_table("provider_configs")
