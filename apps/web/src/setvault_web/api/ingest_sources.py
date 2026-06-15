from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from setvault_core.models.url_rip import RipJob
from setvault_core.services.ingest_sources import (
    SourceDisabledError,
    list_states,
    search_source,
    set_enabled,
)
from setvault_ingest_sources.registry import get_source
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session, require_admin
from setvault_web.schemas.ingest_sources import (
    CandidateOut,
    SetEnabledIn,
    SourceSearchOut,
    SourceStateOut,
    SourceStatesOut,
)

router = APIRouter(tags=["ingest-sources"])


class _SearchIn(BaseModel):
    q: str
    source: str = "youtube"
    limit: int = 20


@router.post("/api/ingest-sources/search", response_model=SourceSearchOut)
async def search(
    body: _SearchIn,
    user: Annotated[object, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
) -> SourceSearchOut:
    try:
        cands = await search_source(session, kind=body.source, query=body.q, limit=body.limit)
    except SourceDisabledError:
        raise HTTPException(status_code=409, detail="source is disabled")
    except Exception:
        raise HTTPException(status_code=502, detail="source search failed")

    ext_ids = [c.external_id for c in cands]
    in_lib: set[str] = set()
    if ext_ids:
        rows = (await session.execute(
            select(RipJob.source_external_id).where(
                RipJob.source_platform == body.source,
                RipJob.source_external_id.in_(ext_ids),
                RipJob.status != "failed",
            )
        )).scalars()
        in_lib = {r for r in rows if r}
    return SourceSearchOut(items=[
        CandidateOut(
            source_kind=c.source_kind, external_id=c.external_id, title=c.title,
            uploader=c.uploader, duration_seconds=c.duration_seconds,
            thumbnail_url=c.thumbnail_url, webpage_url=c.webpage_url,
            already_in_library=c.external_id in in_lib,
        ) for c in cands
    ])


@router.get("/api/admin/ingest-sources", response_model=SourceStatesOut)
async def admin_list(
    _: Annotated[object, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(db_session)],
) -> SourceStatesOut:
    states = await list_states(session)
    return SourceStatesOut(items=[
        SourceStateOut(
            kind=s.kind,
            name=(get_source(s.kind).name if get_source(s.kind) else s.kind),
            enabled=s.enabled, state=s.state,
            consecutive_failures=s.consecutive_failures, last_error=s.last_error,
        ) for s in states
    ])


@router.put("/api/admin/ingest-sources/{kind}", response_model=SourceStateOut)
async def admin_set_enabled(
    kind: str,
    body: SetEnabledIn,
    _: Annotated[object, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(db_session)],
) -> SourceStateOut:
    source = get_source(kind)
    if source is None:
        raise HTTPException(status_code=404, detail="unknown source")
    st = await set_enabled(session, kind, body.enabled)
    await session.commit()
    return SourceStateOut(
        kind=st.kind, name=source.name, enabled=st.enabled, state=st.state,
        consecutive_failures=st.consecutive_failures, last_error=st.last_error,
    )
