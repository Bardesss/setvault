from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from setvault_core.models.catalog import LiveSet
from setvault_core.models.engagement import ActivityEvent, UserSetState
from setvault_core.models.identity import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

router = APIRouter(prefix="/api/me", tags=["me"])


class ContinueItem(BaseModel):
    slug: str
    title: str
    position_seconds: float
    duration_seconds: int | None


class ActivityItem(BaseModel):
    kind: str
    subject_type: str
    subject_id: str | None
    payload: dict
    created_at: str


@router.get("/continue-listening", response_model=list[ContinueItem])
async def continue_listening(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    stmt = (
        select(UserSetState, LiveSet)
        .join(LiveSet, LiveSet.id == UserSetState.live_set_id)
        .where(
            UserSetState.user_id == user.id,
            UserSetState.completed.is_(False),
            LiveSet.deleted_at.is_(None),
        )
        .order_by(UserSetState.updated_at.desc())
        .limit(8)
    )
    rows = (await session.execute(stmt)).all()
    return [
        ContinueItem(
            slug=live.slug,
            title=live.title,
            position_seconds=state.position_seconds,
            duration_seconds=live.duration_seconds,
        )
        for state, live in rows
    ]


@router.get("/activity", response_model=list[ActivityItem])
async def activity(
    _: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    rows = (
        await session.execute(
            select(ActivityEvent).order_by(ActivityEvent.created_at.desc()).limit(30)
        )
    ).scalars().all()
    return [
        ActivityItem(
            kind=e.kind,
            subject_type=e.subject_type,
            subject_id=str(e.subject_id) if e.subject_id else None,
            payload=e.payload,
            created_at=e.created_at.isoformat(),
        )
        for e in rows
    ]
