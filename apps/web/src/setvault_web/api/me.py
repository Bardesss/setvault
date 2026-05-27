from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from setvault_core.models.catalog import LiveSet
from setvault_core.models.engagement import ActivityEvent, UserSetState
from setvault_core.models.identity import NotificationPreference, User
from setvault_core.services.passwords import hash_password, verify_password
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


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12)


@router.post("/change-password", status_code=204)
async def change_password(
    body: ChangePasswordIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    if not user.password_hash or not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="current password incorrect")
    user.password_hash = hash_password(body.new_password)
    await session.commit()


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


class NotificationPreferenceOut(BaseModel):
    kind: str
    channel: Literal["email", "in_app", "both", "off"]
    connector_id: str | None = None


class NotificationPreferencesListOut(BaseModel):
    items: list[NotificationPreferenceOut]


class NotificationPreferenceUpsertIn(BaseModel):
    channel: Literal["email", "in_app", "both", "off"]
    connector_id: str | None = None


_ALLOWED_KINDS = {"account_security", "mention", "comment_reply"}


@router.get("/notification-preferences", response_model=NotificationPreferencesListOut)
async def list_my_prefs(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    rows = (
        await session.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user.id)
        )
    ).scalars().all()
    return NotificationPreferencesListOut(
        items=[
            NotificationPreferenceOut(
                kind=p.kind,
                channel=p.channel,
                connector_id=str(p.connector_id) if p.connector_id else None,
            )
            for p in rows
        ]
    )


@router.put("/notification-preferences/{kind}", response_model=NotificationPreferenceOut)
async def upsert_my_pref(
    kind: str,
    body: NotificationPreferenceUpsertIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    if kind not in _ALLOWED_KINDS:
        raise HTTPException(status_code=400, detail="unknown notification kind")
    existing = (
        await session.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user.id,
                NotificationPreference.kind == kind,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = NotificationPreference(
            user_id=user.id,
            kind=kind,
            channel=body.channel,
            connector_id=uuid.UUID(body.connector_id) if body.connector_id else None,
        )
        session.add(existing)
    else:
        existing.channel = body.channel
        existing.connector_id = uuid.UUID(body.connector_id) if body.connector_id else None
    await session.commit()
    return NotificationPreferenceOut(
        kind=existing.kind,
        channel=existing.channel,
        connector_id=str(existing.connector_id) if existing.connector_id else None,
    )
