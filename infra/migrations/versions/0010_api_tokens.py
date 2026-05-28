"""api_tokens — long-lived scoped tokens for non-cookie clients (RSS, etc.)

Revision ID: 0010_api_tokens
Revises: 0009_url_rip
Create Date: 2026-05-27 00:00:02
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0010_api_tokens"
down_revision = "0009_url_rip"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # api_tokens — per-user scoped tokens stored as sha256 hashes. Plaintext is
    # returned exactly once at mint time; we keep only the digest.
    op.create_table(
        "api_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False, unique=True),
        sa.Column("scopes", postgresql.ARRAY(sa.String()), nullable=False,
                  server_default=sa.text("'{}'::text[]")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_api_tokens_user_active",
        "api_tokens",
        ["user_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.execute(
        "CREATE INDEX ix_api_tokens_scopes_gin ON api_tokens USING gin (scopes)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_api_tokens_scopes_gin")
    op.drop_index("ix_api_tokens_user_active", table_name="api_tokens")
    op.drop_table("api_tokens")
