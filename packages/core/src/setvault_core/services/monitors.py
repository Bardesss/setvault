from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.monitors import Monitor


def _validate(kind: str, query_text: str | None, source_kind: str | None,
              external_id: str | None) -> None:
    if kind == "query":
        if not (query_text and query_text.strip()):
            raise ValueError("query monitor requires query_text")
    elif kind == "entity":
        if not source_kind or not external_id:
            raise ValueError("entity monitor requires source_kind and external_id")
    else:
        raise ValueError(f"unknown monitor kind {kind!r}")


async def create_monitor(
    session: AsyncSession, *, owner_user_id: uuid.UUID, kind: str,
    query_text: str | None, source_kind: str | None, external_id: str | None,
    per_poll_cap: int = 5,
) -> Monitor:
    _validate(kind, query_text, source_kind, external_id)
    m = Monitor(
        owner_user_id=owner_user_id, kind=kind,
        query_text=query_text.strip() if query_text else None,
        source_kind=source_kind, external_id=external_id,
        enabled=True, per_poll_cap=per_poll_cap,
    )
    session.add(m)
    await session.flush()
    return m


async def list_monitors(session: AsyncSession) -> list[Monitor]:
    return list((await session.execute(
        select(Monitor).order_by(Monitor.created_at.desc())
    )).scalars())


async def get_monitor(session: AsyncSession, monitor_id: uuid.UUID) -> Monitor | None:
    return await session.get(Monitor, monitor_id)


async def set_enabled(
    session: AsyncSession, monitor_id: uuid.UUID, enabled: bool,
) -> Monitor | None:
    m = await session.get(Monitor, monitor_id)
    if m is None:
        return None
    m.enabled = enabled
    await session.flush()
    return m


async def delete_monitor(session: AsyncSession, monitor_id: uuid.UUID) -> bool:
    m = await session.get(Monitor, monitor_id)
    if m is None:
        return False
    await session.delete(m)
    await session.flush()
    return True


async def due_monitors(
    session: AsyncSession, *, interval_seconds: int, now: datetime,
) -> list[Monitor]:
    """Enabled monitors never checked or last checked older than the interval."""
    cutoff = now - timedelta(seconds=interval_seconds)
    return list((await session.execute(
        select(Monitor).where(
            Monitor.enabled.is_(True),
            or_(Monitor.last_checked_at.is_(None), Monitor.last_checked_at < cutoff),
        )
    )).scalars())
