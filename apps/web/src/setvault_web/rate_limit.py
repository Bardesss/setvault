from __future__ import annotations

import os
import time

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from setvault_web.config import get_settings

# Dev/CI concession: the e2e helper logs in once per test, blowing through the 5/min
# default. Setting SETVAULT_DEV_SEED=1 (already gating the test-only seed endpoint)
# raises the auth limit so the full Playwright suite can run in one wave.
_AUTH_LIMIT = 100 if os.environ.get("SETVAULT_DEV_SEED") == "1" else 5


def make_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


_redis: Redis | None = None


async def _client() -> Redis:
    global _redis
    if _redis is None:
        _redis = make_redis()
    return _redis


async def hit(key: str, limit: int, window_seconds: int) -> int:
    redis = await _client()
    now_bucket = int(time.time() // window_seconds)
    redis_key = f"rl:{key}:{now_bucket}"
    pipe = redis.pipeline()
    pipe.incr(redis_key, 1)
    pipe.expire(redis_key, window_seconds + 1)
    count, _ = await pipe.execute()
    return int(count)


async def enforce_auth_strict(request: Request) -> None:
    # Fallback string keys the rate-limit bucket; not a bind address.
    ip = (request.client.host if request.client else "0.0.0.0")  # noqa: S104
    count = await hit(f"auth:{ip}", limit=_AUTH_LIMIT, window_seconds=60)
    if count > _AUTH_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="too many auth attempts",
            headers={"Retry-After": "60"},
        )
