from __future__ import annotations

import mimetypes
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from setvault_core.models.catalog import LiveSet, LiveSetTag, MediaRoot, Tag
from setvault_core.models.engagement import UserSetState
from setvault_core.models.identity import User
from setvault_core.schemas.catalog import PartyOut, SeriesOut, VenueOut
from setvault_core.schemas.sets import (
    SetArtistOut,
    SetDetailOut,
    SetListOut,
    SetPatchIn,
    SetSummaryOut,
)
from setvault_core.services.sets import replace_artists, replace_tags
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session, require_admin

router = APIRouter(prefix="/api/sets", tags=["sets"])


async def _tag_names_for(session: AsyncSession, live_id: uuid.UUID) -> list[str]:
    rows = (
        await session.execute(
            select(Tag.name)
            .join(LiveSetTag, LiveSetTag.tag_id == Tag.id)
            .where(LiveSetTag.live_set_id == live_id)
            .order_by(Tag.name)
        )
    ).scalars().all()
    return list(rows)


def _artists_out(live: LiveSet) -> list[SetArtistOut]:
    return [
        SetArtistOut(
            id=str(a.artist.id),
            name=a.artist.name,
            slug=a.artist.slug,
            role=a.role,
        )
        for a in live.artists
    ]


def _venue_out(v) -> VenueOut:
    return VenueOut(
        id=str(v.id),
        slug=v.slug,
        name=v.name,
        kind=v.kind,
        city_or_area=v.city_or_area,
        country=v.country,
        capacity=v.capacity,
        website=v.website,
    )


def _series_out(s) -> SeriesOut:
    return SeriesOut(
        id=str(s.id),
        slug=s.slug,
        name=s.name,
        description=s.description,
        image_url=s.image_url,
    )


def _party_out(p) -> PartyOut:
    return PartyOut(
        id=str(p.id),
        name=p.name,
        slug=p.slug,
        venue=_venue_out(p.venue) if p.venue is not None else None,
        series=_series_out(p.series) if p.series is not None else None,
        date=p.date,
        description=p.description,
    )


@router.get("", response_model=SetListOut)
async def list_sets(
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
    limit: int = 50,
    offset: int = 0,
):
    base = select(LiveSet).where(
        LiveSet.deleted_at.is_(None), LiveSet.status == "published"
    )
    total = (
        await session.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    rows = (
        await session.execute(
            base.order_by(
                LiveSet.date.desc().nullslast(), LiveSet.created_at.desc()
            )
            .limit(limit)
            .offset(offset)
        )
    ).scalars().unique().all()
    items = []
    for r in rows:
        items.append(
            SetSummaryOut(
                id=str(r.id),
                slug=r.slug,
                title=r.title,
                date=r.date,
                duration_seconds=r.duration_seconds,
                set_type=r.set_type,
                status=r.status,
                artists=_artists_out(r),
                tags=await _tag_names_for(session, r.id),
            )
        )
    return SetListOut(items=items, total=int(total))


@router.get("/{slug}", response_model=SetDetailOut)
async def show_set(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(
            select(LiveSet).where(
                LiveSet.slug == slug, LiveSet.deleted_at.is_(None)
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return SetDetailOut(
        id=str(row.id),
        slug=row.slug,
        title=row.title,
        date=row.date,
        duration_seconds=row.duration_seconds,
        set_type=row.set_type,
        status=row.status,
        artists=_artists_out(row),
        tags=await _tag_names_for(session, row.id),
        party=_party_out(row.party) if row.party else None,
        venue=_venue_out(row.venue) if row.venue else None,
        description=row.description,
        audio_stream_url=f"/api/sets/{slug}/stream",
        waveform_url=f"/api/sets/{slug}/waveform" if row.waveform_path else None,
        normalized_lufs=row.normalized_lufs,
    )


@router.patch("/{slug}", response_model=SetDetailOut)
async def edit_set(
    slug: str,
    body: SetPatchIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    live = (
        await session.execute(
            select(LiveSet).where(
                LiveSet.slug == slug, LiveSet.deleted_at.is_(None)
            )
        )
    ).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="not found")
    if body.title is not None:
        live.title = body.title
    if body.date is not None:
        live.date = body.date
    if body.set_type is not None:
        live.set_type = body.set_type
    if body.party_id is not None:
        live.party_id = uuid.UUID(body.party_id)
    if body.venue_id is not None:
        live.venue_id = uuid.UUID(body.venue_id)
    if body.description is not None:
        live.description = body.description
    if body.artist_ids is not None:
        await replace_artists(session, live, body.artist_ids)
    if body.tag_names is not None:
        await replace_tags(session, live, body.tag_names)
    await session.commit()
    return await show_set(slug, session, None)  # type: ignore[arg-type]


@router.delete("/{slug}", status_code=204)
async def delete_set(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    live = (
        await session.execute(
            select(LiveSet).where(
                LiveSet.slug == slug, LiveSet.deleted_at.is_(None)
            )
        )
    ).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="not found")
    now = datetime.now(UTC)
    live.deleted_at = now
    live.purge_after_at = now + timedelta(days=14)
    await session.commit()


@router.get("/{slug}/stream")
async def stream_set(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(
            select(LiveSet).where(
                LiveSet.slug == slug, LiveSet.deleted_at.is_(None)
            )
        )
    ).scalar_one_or_none()
    if row is None or row.streaming_path is None:
        raise HTTPException(status_code=404, detail="not ready")
    root = await session.get(MediaRoot, row.media_root_id)
    path = Path(root.host_path) / row.streaming_path
    # Detect media type from extension so test fixtures (e.g. silent.wav) work too;
    # production sets streaming_path to an .opus file so audio/ogg remains the norm.
    guessed, _ = mimetypes.guess_type(str(path))
    return FileResponse(path, media_type=guessed or "audio/ogg")


@router.get("/{slug}/waveform")
async def waveform(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(
            select(LiveSet).where(
                LiveSet.slug == slug, LiveSet.deleted_at.is_(None)
            )
        )
    ).scalar_one_or_none()
    if row is None or row.waveform_path is None:
        raise HTTPException(status_code=404, detail="not ready")
    root = await session.get(MediaRoot, row.media_root_id)
    return FileResponse(
        Path(root.host_path) / row.waveform_path,
        media_type="application/json",
    )


class StateOut(BaseModel):
    position_seconds: float
    completed: bool


class StateIn(BaseModel):
    position_seconds: float
    completed: bool


@router.get("/{slug}/state", response_model=StateOut)
async def get_state(
    slug: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = (
        await session.execute(
            select(LiveSet).where(LiveSet.slug == slug, LiveSet.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="not found")
    state = await session.get(UserSetState, (user.id, live.id))
    return StateOut(
        position_seconds=state.position_seconds if state else 0.0,
        completed=state.completed if state else False,
    )


@router.put("/{slug}/state", status_code=204)
async def put_state(
    slug: str,
    body: StateIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = (
        await session.execute(
            select(LiveSet).where(LiveSet.slug == slug, LiveSet.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="not found")
    state = await session.get(UserSetState, (user.id, live.id))
    if state is None:
        session.add(
            UserSetState(
                user_id=user.id,
                live_set_id=live.id,
                position_seconds=body.position_seconds,
                completed=body.completed,
            )
        )
    else:
        state.position_seconds = body.position_seconds
        state.completed = body.completed
    await session.commit()
