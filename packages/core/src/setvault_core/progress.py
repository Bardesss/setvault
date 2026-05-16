from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel
from redis import Redis


def channel_for_set(live_set_id: str) -> str:
    return f"sv:progress:set:{live_set_id}"


class ProgressEvent(BaseModel):
    kind: Literal["probe", "fingerprint", "transcode", "normalize", "waveform", "ready", "failed"]
    live_set_id: str
    job_id: str
    progress_pct: int = 0
    message: str | None = None


_publisher: Redis | None = None


def publisher() -> Redis:
    global _publisher
    if _publisher is None:
        _publisher = Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    return _publisher


def publish(event: ProgressEvent) -> None:
    publisher().publish(channel_for_set(event.live_set_id), event.model_dump_json())
