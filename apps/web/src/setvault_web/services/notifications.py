"""Notification dispatch helpers (RQ enqueue + graceful degradation)."""
from __future__ import annotations

import logging
from functools import lru_cache

from redis import Redis
from rq import Queue
from setvault_core.models.system import NotificationConnector
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import Settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=8)
def _queue(redis_url: str) -> Queue:
    return Queue("default", connection=Redis.from_url(redis_url))


async def enqueue_email(
    session: AsyncSession,
    settings: Settings,
    *,
    to: str,
    subject: str,
    text: str,
) -> bool:
    """Enqueue an email via the first enabled SMTP connector.

    Returns True if a job was queued; False if no connector exists or Redis is unreachable.
    """
    row = (
        await session.execute(
            select(NotificationConnector)
            .where(
                NotificationConnector.kind == "smtp",
                NotificationConnector.enabled.is_(True),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is None:
        return False
    try:
        _queue(settings.redis_url).enqueue(
            "setvault_core.jobs.email.send_email_job",
            connector_id=str(row.id),
            to=to,
            subject=subject,
            text=text,
        )
    except Exception:
        logger.exception("failed to enqueue email job")
        return False
    return True
