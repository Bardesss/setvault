"""Worker entrypoint.

Boots an RQ worker on the `default` queue plus an rq-scheduler so periodic
jobs (e.g. MediaRoot health-checks) run on schedule.

Notes on API drift:
  * `rq>=2.0` removed `rq.Connection`; we pass `connection=` directly to
    `Worker` and `Queue` instead.
  * `rq-scheduler.Scheduler.schedule(scheduled_time=..., func=..., interval=...,
    repeat=None)` is the modern signature.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime

from redis import Redis
from rq import Queue, Worker
from rq_scheduler import Scheduler
from setvault_core.db import init_engine

HEALTH_CHECK_FN = "setvault_core.jobs.media_root_health.run_health_checks_sync"
HEALTH_CHECK_INTERVAL_SECONDS = 300  # 5 minutes


def _bootstrap_scheduler(redis: Redis) -> None:
    """Register the periodic MediaRoot health-check job exactly once at boot."""
    scheduler = Scheduler(connection=redis)
    already = {j.func_name for j in scheduler.get_jobs()}
    if HEALTH_CHECK_FN not in already:
        scheduler.schedule(
            scheduled_time=datetime.now(UTC),
            func=HEALTH_CHECK_FN,
            interval=HEALTH_CHECK_INTERVAL_SECONDS,
            repeat=None,
        )


def main() -> None:
    init_engine(os.environ["DATABASE_URL"])
    redis = Redis.from_url(os.environ["REDIS_URL"])
    _bootstrap_scheduler(redis)
    queue = Queue("default", connection=redis)
    Worker([queue], connection=redis).work(with_scheduler=True)


if __name__ == "__main__":
    main()
