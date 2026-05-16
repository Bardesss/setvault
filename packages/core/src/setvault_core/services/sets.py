from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.catalog import LiveSet, LiveSetArtist, LiveSetTag, Tag
from setvault_core.services.catalog import slugify


async def replace_artists(
    session: AsyncSession, live: LiveSet, artist_ids: list[str]
) -> None:
    live.artists.clear()
    for pos, aid in enumerate(artist_ids):
        live.artists.append(
            LiveSetArtist(artist_id=uuid.UUID(aid), position=pos, role="main")
        )


async def replace_tags(
    session: AsyncSession, live: LiveSet, tag_names: list[str]
) -> None:
    await session.execute(
        LiveSetTag.__table__.delete().where(LiveSetTag.live_set_id == live.id)
    )
    for name in tag_names:
        slug = slugify(name)
        tag = (
            await session.execute(select(Tag).where(Tag.slug == slug))
        ).scalar_one_or_none()
        if tag is None:
            tag = Tag(name=name, slug=slug, kind="custom")
            session.add(tag)
            await session.flush()
        session.add(LiveSetTag(live_set_id=live.id, tag_id=tag.id))
