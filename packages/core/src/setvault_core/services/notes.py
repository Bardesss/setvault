from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.engagement_3c import PrivateNote


async def get_note(
    session: AsyncSession, user_id: uuid.UUID, live_set_id: uuid.UUID,
) -> PrivateNote | None:
    return await session.get(PrivateNote, (user_id, live_set_id))


async def upsert_note(
    session: AsyncSession,
    *, user_id: uuid.UUID, live_set_id: uuid.UUID, body_md: str,
) -> PrivateNote:
    existing = await get_note(session, user_id, live_set_id)
    if existing is None:
        existing = PrivateNote(
            user_id=user_id, live_set_id=live_set_id,
            body_md=body_md, updated_at=datetime.now(UTC),
        )
        session.add(existing)
    else:
        existing.body_md = body_md
        existing.updated_at = datetime.now(UTC)
    await session.flush()
    return existing
