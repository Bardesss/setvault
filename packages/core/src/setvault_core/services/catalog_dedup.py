from __future__ import annotations

import re
import unicodedata
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.catalog import Artist, Party, Series, Venue
from setvault_core.services.catalog import EntityKind

_KIND_MODEL = {"artist": Artist, "venue": Venue, "party": Party, "series": Series}


def normalized_name(name: str) -> str:
    """Fold case, strip accents/punctuation, collapse whitespace — a coarse key
    that catches the common auto-ingest near-duplicates ('DJ X' / 'dj  x.')."""
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    alnum = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(alnum.split())


async def find_duplicate_clusters(session: AsyncSession, kind: EntityKind) -> list[list]:
    model = _KIND_MODEL[kind]
    rows = (await session.execute(
        select(model).where(model.merged_into_id.is_(None))
    )).scalars().all()
    groups: dict[str, list] = defaultdict(list)
    for row in rows:
        groups[normalized_name(row.name)].append(row)
    return [members for members in groups.values() if len(members) >= 2]
