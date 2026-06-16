from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from setvault_core.models.identity import User
from setvault_core.models.monitors import Monitor, MonitorDiscovery
from setvault_core.schemas.monitors import (
    DiscoveriesListOut,
    DiscoveryOut,
    MonitorCreate,
    MonitorOut,
    MonitorsListOut,
    MonitorUpdate,
)
from setvault_core.services import monitors as svc
from setvault_core.services.system_config import get_config
from setvault_core.services.url_rip import DuplicateRipError, submit_rip
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitors"])


async def _require_can_monitor(user: User, session: AsyncSession) -> None:
    if user.role == "admin":
        return
    config = await get_config(session)
    if not config.monitors_allow_all_users:
        raise HTTPException(status_code=403, detail="monitoring is admin-only")


def _monitor_out(m: Monitor) -> MonitorOut:
    return MonitorOut(
        id=str(m.id),
        kind=m.kind,
        query_text=m.query_text,
        source_kind=m.source_kind,
        external_id=m.external_id,
        enabled=m.enabled,
        per_poll_cap=m.per_poll_cap,
        last_checked_at=m.last_checked_at,
        created_at=m.created_at,
    )


@router.post("/api/monitors", response_model=MonitorOut, status_code=201)
async def create_monitor(
    payload: MonitorCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    try:
        m = await svc.create_monitor(
            session,
            owner_user_id=user.id,
            kind=payload.kind,
            query_text=payload.query_text,
            source_kind=payload.source_kind,
            external_id=payload.external_id,
            per_poll_cap=payload.per_poll_cap,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await session.commit()
    return _monitor_out(m)


@router.get("/api/monitors", response_model=MonitorsListOut)
async def list_monitors(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    rows = await svc.list_monitors(session)
    return MonitorsListOut(items=[_monitor_out(m) for m in rows])


@router.put("/api/monitors/{monitor_id}", response_model=MonitorOut)
async def update_monitor(
    monitor_id: str,
    payload: MonitorUpdate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    m = await svc.set_enabled(session, uuid.UUID(monitor_id), payload.enabled)
    if m is None:
        raise HTTPException(status_code=404)
    await session.commit()
    return _monitor_out(m)


@router.delete("/api/monitors/{monitor_id}", status_code=204)
async def delete_monitor(
    monitor_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    ok = await svc.delete_monitor(session, uuid.UUID(monitor_id))
    if not ok:
        raise HTTPException(status_code=404)
    await session.commit()


def _disc_out(d: MonitorDiscovery) -> DiscoveryOut:
    return DiscoveryOut(
        id=str(d.id),
        monitor_id=str(d.monitor_id),
        source_kind=d.source_kind,
        external_id=d.external_id,
        title=d.title,
        uploader=d.uploader,
        webpage_url=d.webpage_url,
        duration_seconds=d.duration_seconds,
        thumbnail_url=d.thumbnail_url,
        confidence=d.confidence,
        status=d.status,
        created_at=d.created_at,
    )


@router.get("/api/me/discoveries", response_model=DiscoveriesListOut)
async def list_discoveries(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
    status: str | None = None,
):
    await _require_can_monitor(user, session)
    q = select(MonitorDiscovery).order_by(MonitorDiscovery.created_at.desc())
    if status:
        q = q.where(MonitorDiscovery.status == status)
    rows = (await session.execute(q.limit(200))).scalars().all()
    return DiscoveriesListOut(items=[_disc_out(d) for d in rows])


@router.post("/api/me/discoveries/{discovery_id}/rip", status_code=204)
async def rip_discovery(
    discovery_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    d = await session.get(MonitorDiscovery, uuid.UUID(discovery_id))
    if d is None:
        raise HTTPException(status_code=404)
    if d.status == "pending_review":
        try:
            job = await submit_rip(session, user_id=user.id, url=d.webpage_url)
            d.url_rip_id = job.id
            redis = Redis.from_url(
                os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            )
            Queue("default", connection=redis).enqueue(
                "setvault_core.jobs.url_rip_job.run_rip_job", rip_job_id=str(job.id)
            )
        except DuplicateRipError as exc:
            d.url_rip_id = exc.existing.id
        d.status = "ingested"
        d.decided_at = datetime.now(UTC)
        await session.commit()


@router.post("/api/me/discoveries/{discovery_id}/dismiss", status_code=204)
async def dismiss_discovery(
    discovery_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    await _require_can_monitor(user, session)
    d = await session.get(MonitorDiscovery, uuid.UUID(discovery_id))
    if d is None:
        raise HTTPException(status_code=404)
    d.status = "dismissed"
    d.decided_at = datetime.now(UTC)
    await session.commit()
