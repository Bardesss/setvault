from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.catalog import (
    Artist,
    LiveSet,
    LiveSetArtist,
    Party,
    Series,
    Venue,
)
from setvault_core.models.tracklist import Track
from setvault_core.services.audit import log as audit_log
from setvault_core.services.catalog import EntityKind

_MODEL = {"artist": Artist, "venue": Venue, "party": Party, "series": Series}

# Scalar fields gap-filled from loser into survivor (survivor wins when non-empty).
_SCALAR = {
    "artist": ["country", "bio", "image_url"],
    "venue": ["kind", "city_or_area", "country", "lat", "lon", "capacity", "website"],
    "party": ["date", "description"],
    "series": ["description", "image_url"],
}


async def _repoint_artist(s, survivor_id, loser_id) -> dict:
    moved_tracks, moved_join, deleted_join = [], [], []
    # LiveSetArtist: move loser->survivor, but drop rows that would collide on the
    # composite PK (the set already lists the survivor).
    rows = (await s.execute(
        select(LiveSetArtist).where(LiveSetArtist.artist_id == loser_id)
    )).scalars().all()
    existing = {
        r.live_set_id for r in (await s.execute(
            select(LiveSetArtist).where(LiveSetArtist.artist_id == survivor_id)
        )).scalars().all()
    }
    for r in rows:
        if r.live_set_id in existing:
            deleted_join.append([str(r.live_set_id), str(loser_id)])
            await s.delete(r)
        else:
            r.artist_id = survivor_id
            moved_join.append(str(r.live_set_id))
    await s.flush()
    track_ids = [t.id for t in (await s.execute(
        select(Track).where(Track.primary_artist_id == loser_id)
    )).scalars().all()]
    if track_ids:
        await s.execute(update(Track).where(Track.id.in_(track_ids))
                        .values(primary_artist_id=survivor_id))
        moved_tracks = [str(t) for t in track_ids]
    return {"moved": {"live_set_artists": moved_join, "tracks.primary_artist_id": moved_tracks},
            "deleted_join": deleted_join}


async def _repoint_simple(s, *, loser_id, survivor_id, model, column) -> dict:
    ids = [r[0] for r in (await s.execute(
        select(model.id).where(column == loser_id)
    )).all()]
    if ids:
        await s.execute(update(model).where(model.id.in_(ids)).values({column.key: survivor_id}))
    return {"moved": {f"{model.__tablename__}.{column.key}": [str(i) for i in ids]}}


async def _repoint(s, kind, survivor_id, loser_id) -> dict:
    if kind == "artist":
        return await _repoint_artist(s, survivor_id, loser_id)
    if kind == "venue":
        a = await _repoint_simple(s, loser_id=loser_id, survivor_id=survivor_id,
                                  model=LiveSet, column=LiveSet.venue_id)
        b = await _repoint_simple(s, loser_id=loser_id, survivor_id=survivor_id,
                                  model=Party, column=Party.venue_id)
        return {"moved": {**a["moved"], **b["moved"]}}
    if kind == "party":
        return await _repoint_simple(s, loser_id=loser_id, survivor_id=survivor_id,
                                     model=LiveSet, column=LiveSet.party_id)
    if kind == "series":
        return await _repoint_simple(s, loser_id=loser_id, survivor_id=survivor_id,
                                     model=Party, column=Party.series_id)
    raise ValueError(f"unknown kind {kind}")


def _empty(v) -> bool:
    return v is None or v == "" or v == [] or v == {}


async def merge_entities(
    session: AsyncSession, *, kind: EntityKind,
    survivor_id: uuid.UUID, loser_id: uuid.UUID, actor_id: uuid.UUID | None,
):
    if survivor_id == loser_id:
        raise ValueError("cannot merge an entity into itself")
    if kind not in _MODEL:
        raise ValueError(f"unknown kind: {kind!r}")
    model = _MODEL[kind]
    survivor = await session.get(model, survivor_id)
    loser = await session.get(model, loser_id)
    if survivor is None or loser is None:
        raise ValueError("survivor or loser not found")
    if survivor.merged_into_id is not None or loser.merged_into_id is not None:
        raise ValueError("cannot merge a tombstoned entity")

    manifest = await _repoint(session, kind, survivor_id, loser_id)

    gap_filled = []
    for field in _SCALAR[kind]:
        if _empty(getattr(survivor, field)) and not _empty(getattr(loser, field)):
            setattr(survivor, field, getattr(loser, field))
            gap_filled.append(field)

    if kind == "artist":
        aliases = list(survivor.aliases or [])
        for extra in [loser.name, *(loser.aliases or [])]:
            if extra and extra not in aliases:
                aliases.append(extra)
        survivor.aliases = aliases
        survivor.external_ids = {**(loser.external_ids or {}), **(survivor.external_ids or {})}
        survivor.socials = {**(loser.socials or {}), **(survivor.socials or {})}

    manifest["survivor_id"] = str(survivor_id)
    manifest["gap_filled"] = gap_filled
    loser.merged_into_id = survivor_id
    loser.merged_at = datetime.now(UTC)
    loser.merge_manifest = manifest

    await audit_log(
        session, actor_user_id=actor_id, action=f"{kind}.merged",
        target_type=model.__name__, target_id=str(loser_id),
        after={"survivor_id": str(survivor_id), "manifest": manifest},
    )
    await session.flush()
    return survivor


async def unmerge_entity(
    session: AsyncSession, *, kind: EntityKind, loser_id: uuid.UUID, actor_id: uuid.UUID | None,
):
    model = _MODEL[kind]
    loser = await session.get(model, loser_id)
    if loser is None or loser.merged_into_id is None or loser.merge_manifest is None:
        raise ValueError("entity is not a merged tombstone")
    manifest = loser.merge_manifest

    for table_col, ids in manifest.get("moved", {}).items():
        if not ids:
            continue
        if table_col == "live_set_artists":
            await session.execute(
                update(LiveSetArtist)
                .where(LiveSetArtist.live_set_id.in_([uuid.UUID(i) for i in ids]),
                       LiveSetArtist.artist_id == manifest["survivor_id"])
                .values(artist_id=loser_id)
            )
        elif table_col == "tracks.primary_artist_id":
            await session.execute(update(Track).where(Track.id.in_([uuid.UUID(i) for i in ids]))
                                  .values(primary_artist_id=loser_id))
        elif table_col == "live_sets.venue_id":
            await session.execute(update(LiveSet).where(LiveSet.id.in_([uuid.UUID(i) for i in ids]))
                                  .values(venue_id=loser_id))
        elif table_col == "parties.venue_id":
            await session.execute(update(Party).where(Party.id.in_([uuid.UUID(i) for i in ids]))
                                  .values(venue_id=loser_id))
        elif table_col == "live_sets.party_id":
            await session.execute(update(LiveSet).where(LiveSet.id.in_([uuid.UUID(i) for i in ids]))
                                  .values(party_id=loser_id))
        elif table_col == "parties.series_id":
            await session.execute(update(Party).where(Party.id.in_([uuid.UUID(i) for i in ids]))
                                  .values(series_id=loser_id))
    # recreate join rows that were dropped on PK collision
    for ls_id, _aid in manifest.get("deleted_join", []):
        session.add(LiveSetArtist(live_set_id=uuid.UUID(ls_id), artist_id=loser_id))

    loser.merged_into_id = None
    loser.merged_at = None
    loser.merge_manifest = None
    await audit_log(session, actor_user_id=actor_id, action=f"{kind}.unmerged",
                    target_type=model.__name__, target_id=str(loser_id))
    await session.flush()
    return loser
