from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.schemas.tracklist import (
    TracklistEntryCreateIn,
    TracklistEntryMoveIn,
    TracklistEntryOut,
    TracklistEntryPatchIn,
)
from setvault_core.services.audit import log as audit_log
from setvault_core.services.tracklist import (
    InvalidPosition,
    create_entry,
    delete_entry,
    list_entries,
    reorder_entries,
    update_entry,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

router = APIRouter(prefix="/api/sets", tags=["tracklist"])


class TracklistOut(BaseModel):
    entries: list[TracklistEntryOut]


def _to_out(e: TracklistEntry) -> TracklistEntryOut:
    return TracklistEntryOut(
        id=str(e.id),
        position=e.position,
        start_seconds=e.start_seconds,
        end_seconds=e.end_seconds,
        raw_label=e.raw_label,
        edit_notes=e.edit_notes,
        status=e.status,
        confidence=e.confidence,
        track_id=str(e.track_id) if e.track_id else None,
        mashup_with=[str(x) for x in (e.mashup_with or [])],
    )


async def _load_set(session: AsyncSession, slug: str) -> LiveSet:
    live = (await session.execute(
        select(LiveSet).where(LiveSet.slug == slug, LiveSet.deleted_at.is_(None))
    )).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="not found")
    return live


@router.get("/{slug}/tracklist", response_model=TracklistOut)
async def get_tracklist(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[User, Depends(current_user)],
):
    live = await _load_set(session, slug)
    entries = await list_entries(session, live.id)
    return TracklistOut(entries=[_to_out(e) for e in entries])


@router.post("/{slug}/tracklist/entries", response_model=TracklistEntryOut, status_code=201)
async def create_tracklist_entry(
    slug: str,
    body: TracklistEntryCreateIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _load_set(session, slug)
    try:
        entry = await create_entry(
            session, live.id,
            user_id=user.id,
            start_seconds=body.start_seconds,
            raw_label=body.raw_label,
            position=body.position,
            end_seconds=body.end_seconds,
            edit_notes=body.edit_notes,
        )
    except InvalidPosition as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await audit_log(
        session, actor_user_id=user.id, actor_kind="user",
        action="tracklist.entry.created",
        target_type="tracklist_entry", target_id=str(entry.id),
        after={"live_set_id": str(live.id), "position": entry.position,
               "raw_label": entry.raw_label},
    )
    await session.commit()
    return _to_out(entry)


@router.patch("/{slug}/tracklist/entries/{entry_id}", response_model=TracklistEntryOut)
async def patch_tracklist_entry(
    slug: str,
    entry_id: str,
    body: TracklistEntryPatchIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _load_set(session, slug)
    entry = (await session.execute(
        select(TracklistEntry).where(
            TracklistEntry.id == uuid.UUID(entry_id),
            TracklistEntry.live_set_id == live.id,
        )
    )).scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="entry not found")
    before = {"raw_label": entry.raw_label, "start_seconds": entry.start_seconds}
    await update_entry(
        session, entry,
        start_seconds=body.start_seconds,
        end_seconds=body.end_seconds,
        raw_label=body.raw_label,
        edit_notes=body.edit_notes,
        mashup_with=[uuid.UUID(x) for x in body.mashup_with] if body.mashup_with else None,
    )
    after = {"raw_label": entry.raw_label, "start_seconds": entry.start_seconds}
    await audit_log(
        session, actor_user_id=user.id, actor_kind="user",
        action="tracklist.entry.updated",
        target_type="tracklist_entry", target_id=str(entry.id),
        before=before, after=after,
    )
    await session.commit()
    return _to_out(entry)


@router.patch("/{slug}/tracklist/entries/{entry_id}/move", status_code=204)
async def move_tracklist_entry(
    slug: str,
    entry_id: str,
    body: TracklistEntryMoveIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _load_set(session, slug)
    try:
        await reorder_entries(session, live.id, entry_id=entry_id,
                              after_position=body.after_position)
    except InvalidPosition as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await session.commit()


@router.delete("/{slug}/tracklist/entries/{entry_id}", status_code=204)
async def delete_tracklist_entry(
    slug: str,
    entry_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _load_set(session, slug)
    entry = (await session.execute(
        select(TracklistEntry).where(
            TracklistEntry.id == uuid.UUID(entry_id),
            TracklistEntry.live_set_id == live.id,
        )
    )).scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="entry not found")
    entry_id_str = str(entry.id)
    raw_label = entry.raw_label
    await delete_entry(session, entry)
    await audit_log(
        session, actor_user_id=user.id, actor_kind="user",
        action="tracklist.entry.deleted",
        target_type="tracklist_entry", target_id=entry_id_str,
        before={"raw_label": raw_label},
    )
    await session.commit()
