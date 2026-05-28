"""5a — watch_folders + unmatched_files (Phase 5A watch-folder cluster)

Revision ID: 0012_5a
Revises: 0011_embed
Create Date: 2026-05-28 12:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012_5a"
down_revision = "0011_embed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # watch_folders — admin-configured filesystem locations the watcher
    # subscribes to. Each maps to a target MediaRoot for the ingested set.
    op.create_table(
        "watch_folders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("host_path", sa.String(length=2048), nullable=False, unique=True),
        sa.Column("target_media_root_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("media_roots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_health_check_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_health_status", sa.String(length=16),
                  nullable=False, server_default="unknown"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.execute(
        "CREATE INDEX ix_watch_folders_enabled ON watch_folders (enabled) "
        "WHERE enabled = true"
    )

    # unmatched_files — queue of files the ingest pipeline couldn't auto-match.
    # Admin resolves each (link to existing set / create as draft / discard).
    op.create_table(
        "unmatched_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("watch_folder_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("watch_folders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.String(length=2048), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("audio_info", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        # pending | linked_to_set | created_as_draft | discarded
        sa.Column("resolution", sa.String(length=24),
                  nullable=False, server_default="pending"),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_to_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("error_text", sa.Text, nullable=True),
    )
    op.create_index(
        "ix_unmatched_files_pending",
        "unmatched_files",
        ["watch_folder_id", sa.text("detected_at desc")],
        postgresql_where=sa.text("resolution = 'pending'"),
    )
    op.create_index(
        "ix_unmatched_files_watch_folder",
        "unmatched_files",
        ["watch_folder_id"],
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_unmatched_files_pending")
    op.drop_index("ix_unmatched_files_watch_folder", table_name="unmatched_files")
    op.drop_table("unmatched_files")
    op.execute("DROP INDEX IF EXISTS ix_watch_folders_enabled")
    op.drop_table("watch_folders")
