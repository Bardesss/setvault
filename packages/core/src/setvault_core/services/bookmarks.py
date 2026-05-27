from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.engagement_3c import Bookmark


async def list_bookmarks_for_user(session: AsyncSession, user_id: uuid.UUID) -> list[Bookmark]:
    return list((await session.execute(
        select(Bookmark).where(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
    )).scalars().all())


async def list_bookmarks_for_set(
    session: AsyncSession, user_id: uuid.UUID, live_set_id: uuid.UUID,
) -> list[Bookmark]:
    return list((await session.execute(
        select(Bookmark).where(
            Bookmark.user_id == user_id, Bookmark.live_set_id == live_set_id,
        ).order_by(Bookmark.position_seconds.nullsfirst())
    )).scalars().all())


async def create_bookmark(
    session: AsyncSession,
    *, user_id: uuid.UUID, live_set_id: uuid.UUID,
    position_seconds: int | None, label: str | None,
) -> Bookmark:
    b = Bookmark(
        user_id=user_id, live_set_id=live_set_id,
        position_seconds=position_seconds, label=label,
        created_at=datetime.now(UTC),
    )
    session.add(b)
    await session.flush()
    return b
