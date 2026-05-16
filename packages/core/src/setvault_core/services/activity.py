from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.engagement import ActivityEvent


async def record(
    session: AsyncSession,
    *,
    kind: str,
    subject_type: str,
    subject_id: uuid.UUID,
    user_id: uuid.UUID | None,
    payload: dict | None = None,
) -> ActivityEvent:
    event = ActivityEvent(
        kind=kind,
        subject_type=subject_type,
        subject_id=subject_id,
        user_id=user_id,
        payload=payload or {},
    )
    session.add(event)
    return event
