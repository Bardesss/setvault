#!/usr/bin/env bash
# Bring the database to a migrated state, both modes. Run by the init-db
# s6 oneshot (after the postgres longrun is "up"). Idempotent.
set -e
PGBIN=/usr/lib/postgresql/18/bin

# 1) Wait until the effective Postgres accepts connections.
attempts=0; max=60
until "${PGBIN}/pg_isready" -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT:-5432}" -q; do
  attempts=$((attempts + 1))
  if [ "${attempts}" -ge "${max}" ]; then
    echo "[setvault] postgres not ready after ${max} tries; bailing" >&2
    exit 1
  fi
  sleep 2
done

# 2) Embedded first boot: ensure database + role password (local trust socket).
if [ "${SETVAULT_PG_EMBEDDED}" = "1" ]; then
  DB="${POSTGRES_DB:-setvault}"
  has_db="$(s6-setuidgid "${PUID:-1000}:${PGID:-1000}" \
    "${PGBIN}/psql" -h /tmp -U setvault -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${DB}'" || true)"
  if [ "${has_db}" != "1" ]; then
    s6-setuidgid "${PUID:-1000}:${PGID:-1000}" \
      "${PGBIN}/psql" -h /tmp -U setvault -d postgres -c \
      "CREATE DATABASE ${DB} OWNER setvault"
  fi
  s6-setuidgid "${PUID:-1000}:${PGID:-1000}" \
    "${PGBIN}/psql" -h /tmp -U setvault -d postgres -c \
    "ALTER USER setvault PASSWORD '${POSTGRES_PASSWORD:-setvault}'"
fi

# 3) Migrations (both modes).
cd /srv
attempts=0; max=30
until s6-setuidgid "${PUID:-1000}:${PGID:-1000}" /srv/.venv/bin/alembic upgrade head; do
  attempts=$((attempts + 1))
  if [ "${attempts}" -ge "${max}" ]; then
    echo "[setvault] alembic failed after ${max} tries; bailing" >&2
    exit 1
  fi
  echo "[setvault] alembic retry ${attempts}/${max}" >&2
  sleep 2
done
echo "[setvault] migrations up-to-date" >&2
