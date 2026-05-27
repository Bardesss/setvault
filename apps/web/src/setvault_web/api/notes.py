from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from setvault_core.schemas.notes import PrivateNoteOut, PrivateNoteUpsertIn
from setvault_core.services.comments import render_markdown_safe
from setvault_core.services.notes import get_note, upsert_note
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

router = APIRouter(tags=["notes"])


async def _resolve_set(session: AsyncSession, slug: str) -> LiveSet:
    live = (await session.execute(
        select(LiveSet).where(LiveSet.slug == slug, LiveSet.deleted_at.is_(None))
    )).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404)
    return live


@router.get("/api/sets/{slug}/note", response_model=PrivateNoteOut)
async def get_private_note(
    slug: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _resolve_set(session, slug)
    note = await get_note(session, user.id, live.id)
    if note is None:
        return PrivateNoteOut(body_md="", body_html="", updated_at=None)
    return PrivateNoteOut(
        body_md=note.body_md,
        body_html=render_markdown_safe(note.body_md),
        updated_at=note.updated_at,
    )


@router.put("/api/sets/{slug}/note", response_model=PrivateNoteOut)
async def put_private_note(
    slug: str,
    body: PrivateNoteUpsertIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    live = await _resolve_set(session, slug)
    note = await upsert_note(session, user_id=user.id, live_set_id=live.id, body_md=body.body_md)
    await session.commit()
    return PrivateNoteOut(
        body_md=note.body_md,
        body_html=render_markdown_safe(note.body_md),
        updated_at=note.updated_at,
    )
