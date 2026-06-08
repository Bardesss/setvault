#!/usr/bin/env bash
# Unit tests for mode-detect.sh — pure, no Docker.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "${HERE}/../lib/mode-detect.sh"

fail=0
check() { # desc expected actual
  if [ "$2" = "$3" ]; then echo "ok   - $1"; else echo "FAIL - $1: expected [$2] got [$3]"; fail=1; fi
}

# Case 1: nothing set -> fully bundled.
( unset DATABASE_URL REDIS_URL POSTGRES_HOST
  eval "$(setvault_compute_mode)"
  check "bundled: pg embedded"    1 "${SETVAULT_PG_EMBEDDED}"
  check "bundled: redis embedded" 1 "${SETVAULT_REDIS_EMBEDDED}"
  check "bundled: caddy enabled"  1 "${SETVAULT_CADDY_ENABLED}"
  check "bundled: uvicorn 8081"   8081 "${SETVAULT_UVICORN_PORT}"
  check "bundled: pg host"        127.0.0.1 "${POSTGRES_HOST}"
  check "bundled: redis url"      "redis://127.0.0.1:6379/0" "${REDIS_URL}"
) || fail=1

# Case 2: external DATABASE_URL -> pg external, redis still bundled, no caddy/port move.
( unset REDIS_URL POSTGRES_HOST
  export DATABASE_URL="postgresql+asyncpg://u:p@db.example:5432/x"
  eval "$(setvault_compute_mode)"
  check "extpg: pg external"      0 "${SETVAULT_PG_EMBEDDED}"
  check "extpg: redis embedded"   1 "${SETVAULT_REDIS_EMBEDDED}"
  check "extpg: caddy disabled"   0 "${SETVAULT_CADDY_ENABLED}"
  check "extpg: uvicorn 1970"     1970 "${SETVAULT_UVICORN_PORT}"
) || fail=1

# Case 3: external REDIS_URL only -> redis external, pg bundled (caddy on, port 8081).
( unset DATABASE_URL POSTGRES_HOST
  export REDIS_URL="redis://redis.example:6379/0"
  eval "$(setvault_compute_mode)"
  check "extredis: pg embedded"    1 "${SETVAULT_PG_EMBEDDED}"
  check "extredis: redis external" 0 "${SETVAULT_REDIS_EMBEDDED}"
  check "extredis: redis url kept" "redis://redis.example:6379/0" "${REDIS_URL}"
) || fail=1

# Case 4: loopback REDIS_URL counts as embedded.
( unset DATABASE_URL POSTGRES_HOST
  export REDIS_URL="redis://127.0.0.1:6379/0"
  eval "$(setvault_compute_mode)"
  check "loopback redis embedded"  1 "${SETVAULT_REDIS_EMBEDDED}"
) || fail=1

# Case 5: external POSTGRES_HOST (compose service name) -> pg external.
( unset DATABASE_URL REDIS_URL
  export POSTGRES_HOST="postgres"
  eval "$(setvault_compute_mode)"
  check "host=postgres -> external" 0 "${SETVAULT_PG_EMBEDDED}"
) || fail=1

exit "${fail}"
