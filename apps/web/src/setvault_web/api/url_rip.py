from __future__ import annotations

import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from setvault_core.models.url_rip import RipJob
from setvault_core.schemas.url_rip import RipJobOut, RipJobsListOut, RipSubmitIn
from setvault_core.services import url_rip as _service
from setvault_core.services.audit import log as audit_log
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

router = APIRouter(tags=["url_rip"])


def _redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def _queue() -> Queue:
    return Queue("default", connection=Redis.from_url(_redis_url()))


def _to_out(job: RipJob, *, live_set_slug: str | None = None) -> RipJobOut:
    return RipJobOut(
        id=str(job.id),
        live_set_id=str(job.live_set_id) if job.live_set_id else None,
        live_set_slug=live_set_slug,
        source_url=job.source_url,
        source_external_id=job.source_external_id,
        source_platform=job.source_platform,
        status=job.status,
        progress_pct=job.progress_pct,
        message=job.message,
        error_text=job.error_text,
        probed_metadata=job.probed_metadata or {},
        ytdlp_version=job.ytdlp_version,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@router.post("/api/sets/url-rip", response_model=RipJobOut, status_code=201)
async def submit_url_rip(
    body: RipSubmitIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    try:
        job = await _service.submit_rip(session, user_id=user.id, url=body.url)
    except _service.DuplicateRipError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"rip already in progress: {exc.existing.id}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        _queue().enqueue(
            "setvault_core.jobs.url_rip_job.run_rip_job",
            rip_job_id=str(job.id),
        )
    except Exception as exc:
        # If Redis is down we still keep the RipJob row so the user sees the
        # failure and can retry. Mark it failed inline.
        job.status = "failed"
        job.error_text = f"failed to enqueue worker: {exc}"
        await session.flush()

    await audit_log(
        session, actor_user_id=user.id, actor_kind="user",
        action="set.url_rip_submitted",
        target_type="rip_job", target_id=str(job.id),
        after={"url": body.url, "platform": job.source_platform},
    )
    await session.commit()
    return _to_out(job)


@router.get("/api/me/rip-jobs", response_model=RipJobsListOut)
async def my_rip_jobs(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
    status: str | None = None,
    limit: int = 50,
):
    q = select(RipJob).where(RipJob.submitted_by == user.id)
    if status == "active":
        q = q.where(RipJob.status.not_in(("ready", "failed")))
    q = q.order_by(RipJob.created_at.desc()).limit(limit)
    rows = (await session.execute(q)).scalars().all()

    set_ids = [r.live_set_id for r in rows if r.live_set_id]
    sets_by_id: dict[uuid.UUID, str] = {}
    if set_ids:
        live_rows = (await session.execute(
            select(LiveSet).where(LiveSet.id.in_(set_ids))
        )).scalars().all()
        sets_by_id = {ls.id: ls.slug for ls in live_rows}

    return RipJobsListOut(items=[
        _to_out(r, live_set_slug=sets_by_id.get(r.live_set_id) if r.live_set_id else None)
        for r in rows
    ])
