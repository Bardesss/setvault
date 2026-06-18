from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.catalog import (
    Artist,
    LiveSet,
    LiveSetArtist,
    Party,
    Series,
    Venue,
)
from setvault_core.models.tracklist import Track
from setvault_core.services.catalog_dedup import find_duplicate_clusters
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/admin/catalog", tags=["admin"])

_MODEL = {"artists": Artist, "venues": Venue, "parties": Party, "series": Series}
_NAME = {"artists": "artist", "venues": "venue", "parties": "party", "series": "series"}
_REF: dict[str, list[tuple]] = {
    "artists": [
        (LiveSetArtist, LiveSetArtist.artist_id),
        (Track, Track.primary_artist_id),
    ],
    "venues": [(LiveSet, LiveSet.venue_id), (Party, Party.venue_id)],
    "parties": [(LiveSet, LiveSet.party_id)],
    "series": [(Party, Party.series_id)],
}


async def _ref_count(session: AsyncSession, kind: str, entity_id) -> int:
    total = 0
    for ref_model, ref_col in _REF[kind]:
        total += int(
            (
                await session.execute(
                    select(func.count()).select_from(ref_model).where(ref_col == entity_id)
                )
            ).scalar_one()
        )
    return total


def _row(kind: str, e, ref_count: int) -> dict:
    return {"id": str(e.id), "name": e.name, "slug": e.slug, "ref_count": ref_count}


@router.get("/{kind}/duplicates")
async def list_duplicates(
    kind: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    name = _NAME.get(kind)
    if name is None:
        raise HTTPException(status_code=404, detail="unknown kind")
    clusters = await find_duplicate_clusters(session, kind=name)
    out = []
    for cluster in clusters:
        out.append([_row(kind, e, await _ref_count(session, kind, e.id)) for e in cluster])
    return {"clusters": out}


@router.get("/{kind}/merged")
async def list_merged(
    kind: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    model = _MODEL.get(kind)
    if model is None:
        raise HTTPException(status_code=404, detail="unknown kind")
    rows = (
        await session.execute(
            select(model)
            .where(model.merged_into_id.is_not(None))
            .order_by(model.merged_at.desc())
            .limit(500)
        )
    ).scalars().all()

    # Batch-load survivor names in one query
    survivor_ids = {r.merged_into_id for r in rows if r.merged_into_id is not None}
    survivor_name_map: dict = {}
    if survivor_ids:
        survivor_rows = (
            await session.execute(
                select(model.id, model.name).where(model.id.in_(survivor_ids))
            )
        ).all()
        survivor_name_map = {r.id: r.name for r in survivor_rows}

    items = [
        {
            "id": str(r.id),
            "name": r.name,
            "slug": r.slug,
            "merged_at": r.merged_at.isoformat() if r.merged_at is not None else None,
            "survivor_id": str(r.merged_into_id),
            "survivor_name": survivor_name_map.get(r.merged_into_id),
        }
        for r in rows
    ]
    return {"items": items}


@router.get("/{kind}")
async def list_entities(
    kind: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    model = _MODEL.get(kind)
    if model is None:
        raise HTTPException(status_code=404, detail="unknown kind")
    rows = (
        await session.execute(
            select(model).where(model.merged_into_id.is_(None)).order_by(model.name).limit(500)
        )
    ).scalars().all()
    items = [_row(kind, e, await _ref_count(session, kind, e.id)) for e in rows]
    return {"items": items}
