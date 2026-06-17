from __future__ import annotations

import re
import unicodedata
import uuid
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.catalog import LiveSet, LiveSetArtist, Party

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = _SLUG_NON_ALNUM.sub("-", norm.lower()).strip("-")
    return slug or "item"


EntityKind = Literal["artist", "venue", "party", "series"]


async def list_sets_for_entity(
    session: AsyncSession, *, kind: EntityKind, entity_id: uuid.UUID,
) -> list[LiveSet]:
    """Published, non-deleted LiveSets referencing the entity, newest first."""
    q = select(LiveSet).where(
        LiveSet.deleted_at.is_(None), LiveSet.status == "published",
    )
    if kind == "artist":
        q = q.join(LiveSetArtist, LiveSetArtist.live_set_id == LiveSet.id).where(
            LiveSetArtist.artist_id == entity_id,
        )
    elif kind == "venue":
        q = q.where(LiveSet.venue_id == entity_id)
    elif kind == "party":
        q = q.where(LiveSet.party_id == entity_id)
    elif kind == "series":
        q = q.join(Party, Party.id == LiveSet.party_id).where(Party.series_id == entity_id)
    q = q.order_by(LiveSet.date.desc().nullslast(), LiveSet.created_at.desc())
    return list((await session.execute(q)).scalars().unique().all())
