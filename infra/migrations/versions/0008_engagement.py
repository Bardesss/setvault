"""engagement — comments + bookmarks + private notes + in-app notifications

Revision ID: 0008_engagement
Revises: 0007_providers
Create Date: 2026-05-17 00:00:02
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_engagement"
down_revision = "0007_providers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Comments
    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("position_seconds", sa.Integer, nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("mentions_user_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
                  nullable=False, server_default="{}"),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_comments_live_set_created",
                    "comments", ["live_set_id", sa.text("created_at desc")])
    op.create_index("ix_comments_mentions",
                    "comments", ["mentions_user_ids"], postgresql_using="gin")

    # Bookmarks
    op.create_table(
        "bookmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position_seconds", sa.Integer, nullable=True),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    # Unique (user, set, position_seconds) with coalesce so null = "favorite set"
    op.execute(
        "CREATE UNIQUE INDEX ix_bookmarks_uniq "
        "ON bookmarks (user_id, live_set_id, coalesce(position_seconds, -1))"
    )

    # Private notes — composite PK
    op.create_table(
        "private_notes",
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("body_md", sa.Text, nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )

    # In-app notifications
    op.create_table(
        "in_app_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("subject_type", sa.String(32), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_in_app_notifications_user_created",
                    "in_app_notifications", ["user_id", sa.text("created_at desc")])
    op.execute(
        "CREATE INDEX ix_in_app_notifications_unread "
        "ON in_app_notifications (user_id) WHERE read_at IS NULL"
    )

    # Notification kind: confirmed stored as a plain String column (Phase 2A
    # Literal-as-String pattern), not a native Postgres enum, so no
    # ALTER TYPE notification_kind ADD VALUE step is required here.


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_in_app_notifications_unread")
    op.drop_table("in_app_notifications")
    op.drop_table("private_notes")
    op.execute("DROP INDEX IF EXISTS ix_bookmarks_uniq")
    op.drop_table("bookmarks")
    op.drop_table("comments")
