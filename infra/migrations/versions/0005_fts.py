"""fts

Revision ID: 0005_fts
Revises: 1ab3109cc1d5
Create Date: 2026-05-15 00:00:00
"""
from alembic import op

revision = "0005_fts"
down_revision = "1ab3109cc1d5"
branch_labels = None
depends_on = None


# asyncpg refuses multi-statement prepared statements, so each ALTER / CREATE
# INDEX is issued as a separate op.execute() call.
#
# Postgres requires the expression in a STORED generated column to be IMMUTABLE.
# array_to_string() is STABLE (not IMMUTABLE), so to build a tsvector that
# includes the artists.aliases array we wrap it in a small SQL function marked
# IMMUTABLE. Inputs are text[] -> tsvector via to_tsvector('simple', ...).

ARTISTS_TSV_FN = """
CREATE OR REPLACE FUNCTION setvault_artists_tsv(name text, aliases text[])
RETURNS tsvector AS $$
  SELECT setweight(to_tsvector('simple', coalesce($1, '')), 'A')
      || setweight(to_tsvector('simple',
            coalesce(array_to_string(coalesce($2, ARRAY[]::text[]), ' '), '')), 'B')
$$ LANGUAGE sql IMMUTABLE
"""
ARTISTS_TSV_FN_DROP = "DROP FUNCTION IF EXISTS setvault_artists_tsv(text, text[])"

SETS_COLUMN = """
ALTER TABLE live_sets ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(description, '')), 'C')
  ) STORED
"""
SETS_INDEX = "CREATE INDEX ix_live_sets_search_tsv ON live_sets USING gin (search_tsv)"

ARTISTS_COLUMN = """
ALTER TABLE artists ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (setvault_artists_tsv(name, aliases)) STORED
"""
ARTISTS_INDEX = "CREATE INDEX ix_artists_search_tsv ON artists USING gin (search_tsv)"

PARTIES_COLUMN = """
ALTER TABLE parties ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (setweight(to_tsvector('simple', coalesce(name, '')), 'A')) STORED
"""
PARTIES_INDEX = "CREATE INDEX ix_parties_search_tsv ON parties USING gin (search_tsv)"

VENUES_COLUMN = """
ALTER TABLE venues ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(name, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(city_or_area, '')), 'B')
  ) STORED
"""
VENUES_INDEX = "CREATE INDEX ix_venues_search_tsv ON venues USING gin (search_tsv)"

SERIES_COLUMN = """
ALTER TABLE series ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (setweight(to_tsvector('simple', coalesce(name, '')), 'A')) STORED
"""
SERIES_INDEX = "CREATE INDEX ix_series_search_tsv ON series USING gin (search_tsv)"


def upgrade() -> None:
    # Helper function must exist before the artists generated column references it.
    op.execute(ARTISTS_TSV_FN)
    for sql in (
        SETS_COLUMN, SETS_INDEX,
        ARTISTS_COLUMN, ARTISTS_INDEX,
        PARTIES_COLUMN, PARTIES_INDEX,
        VENUES_COLUMN, VENUES_INDEX,
        SERIES_COLUMN, SERIES_INDEX,
    ):
        op.execute(sql)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_series_search_tsv")
    op.execute("ALTER TABLE series DROP COLUMN IF EXISTS search_tsv")
    op.execute("DROP INDEX IF EXISTS ix_venues_search_tsv")
    op.execute("ALTER TABLE venues DROP COLUMN IF EXISTS search_tsv")
    op.execute("DROP INDEX IF EXISTS ix_parties_search_tsv")
    op.execute("ALTER TABLE parties DROP COLUMN IF EXISTS search_tsv")
    op.execute("DROP INDEX IF EXISTS ix_artists_search_tsv")
    op.execute("ALTER TABLE artists DROP COLUMN IF EXISTS search_tsv")
    op.execute("DROP INDEX IF EXISTS ix_live_sets_search_tsv")
    op.execute("ALTER TABLE live_sets DROP COLUMN IF EXISTS search_tsv")
    op.execute(ARTISTS_TSV_FN_DROP)
