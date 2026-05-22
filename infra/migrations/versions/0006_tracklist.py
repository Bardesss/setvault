"""tracklist

Revision ID: 0006_tracklist
Revises: 0005_fts
Create Date: 2026-05-17 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_tracklist"
down_revision = "0005_fts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Labels
    op.create_table(
        "labels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("external_ids", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("enrichment_status", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_labels_slug", "labels", ["slug"])

    # Releases
    op.create_table(
        "releases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("label_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("labels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("catalog_number", sa.String(64), nullable=True),
        sa.Column("release_date", sa.Date, nullable=True),
        sa.Column("cover_url", sa.String(2048), nullable=True),
        sa.Column("external_ids", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("enrichment_status", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_releases_label_id", "releases", ["label_id"])
    op.create_index("ix_releases_external_ids", "releases", ["external_ids"],
                    postgresql_using="gin")

    # Tracks
    op.create_table(
        "tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("primary_artist_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("artists.id", ondelete="SET NULL"), nullable=True),
        sa.Column("additional_artists", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("mix_name", sa.String(255), nullable=True),
        sa.Column("label_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("labels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("release_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("releases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("bpm", sa.Float, nullable=True),
        sa.Column("key", sa.String(8), nullable=True),
        sa.Column("isrc", sa.String(16), nullable=True),
        sa.Column("external_ids", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("enrichment_status", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tracks_primary_artist_id", "tracks", ["primary_artist_id"])
    op.create_index("ix_tracks_isrc", "tracks", ["isrc"])
    op.create_index("ix_tracks_external_ids", "tracks", ["external_ids"],
                    postgresql_using="gin")

    # ReleaseTrack m2m
    op.create_table(
        "release_tracks",
        sa.Column("release_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("releases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("track_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
    )

    # Tracklist entries
    op.create_table(
        "tracklist_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("start_seconds", sa.Integer, nullable=False),
        sa.Column("end_seconds", sa.Integer, nullable=True),
        sa.Column("track_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("raw_label", sa.String(1024), nullable=False),
        sa.Column("mashup_with", postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
                  nullable=False, server_default="{}"),
        sa.Column("edit_notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="raw"),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    # Deferrable so reorder / insert can renumber positions within a transaction
    # without tripping the constraint on intermediate (duplicate) states; it is
    # validated once at commit.
    op.create_unique_constraint(
        "uq_tracklist_entries_live_set_position",
        "tracklist_entries", ["live_set_id", "position"],
        deferrable=True, initially="DEFERRED",
    )
    op.create_index("ix_tracklist_entries_track_id",
                    "tracklist_entries", ["track_id"])

    # Tracklist import jobs
    op.create_table(
        "tracklist_import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("live_set_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False),  # paste|url_1001tl|ocr
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="queued"),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tracklist_import_jobs_live_set_id",
                    "tracklist_import_jobs", ["live_set_id"])


def downgrade() -> None:
    op.drop_table("tracklist_import_jobs")
    op.drop_table("tracklist_entries")
    op.drop_table("release_tracks")
    op.drop_table("tracks")
    op.drop_table("releases")
    op.drop_table("labels")
