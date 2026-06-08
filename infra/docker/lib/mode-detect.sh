#!/usr/bin/env bash
# Pure mode-detection logic for SetVault's single image.
#
# setvault_compute_mode reads the relevant env vars and echoes a block of
# `KEY=value` export statements the caller can `eval`. No side effects, so
# it is unit-testable without a container.
#
# Decision rules:
#   - Postgres is EXTERNAL if DATABASE_URL is set, or POSTGRES_HOST is set to
#     a non-loopback host. Otherwise EMBEDDED (and POSTGRES_HOST=127.0.0.1).
#   - Redis is EXTERNAL if REDIS_URL is set to a non-loopback target.
#     Otherwise EMBEDDED (and REDIS_URL=redis://127.0.0.1:6379/0).
#   - Caddy + the internal uvicorn port (8081) follow PG embedded (the
#     single-container signal). External PG => uvicorn public on 1970, no Caddy.
setvault_compute_mode() {
  local pg_embedded=1 redis_embedded=1 pg_host redis_url uvicorn_port caddy_enabled

  pg_host="${POSTGRES_HOST:-}"
  if [ -n "${DATABASE_URL:-}" ]; then
    pg_embedded=0
  elif [ -n "${pg_host}" ] && [ "${pg_host}" != "127.0.0.1" ] && [ "${pg_host}" != "localhost" ]; then
    pg_embedded=0
  else
    pg_embedded=1
    pg_host="127.0.0.1"
  fi

  redis_url="${REDIS_URL:-}"
  if [ -n "${redis_url}" ] && ! printf '%s' "${redis_url}" | grep -qE '://(127\.0\.0\.1|localhost)(:|/|$)'; then
    redis_embedded=0
  else
    redis_embedded=1
    redis_url="redis://127.0.0.1:6379/0"
  fi

  if [ "${pg_embedded}" = "1" ]; then
    uvicorn_port=8081
    caddy_enabled=1
  else
    uvicorn_port=1970
    caddy_enabled=0
  fi

  printf 'SETVAULT_PG_EMBEDDED=%s\n' "${pg_embedded}"
  printf 'SETVAULT_REDIS_EMBEDDED=%s\n' "${redis_embedded}"
  printf 'SETVAULT_CADDY_ENABLED=%s\n' "${caddy_enabled}"
  printf 'SETVAULT_UVICORN_PORT=%s\n' "${uvicorn_port}"
  printf 'POSTGRES_HOST=%s\n' "${pg_host}"
  printf 'REDIS_URL=%s\n' "${redis_url}"
}
