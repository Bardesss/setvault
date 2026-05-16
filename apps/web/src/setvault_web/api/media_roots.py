from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.catalog import MediaRoot
from setvault_core.schemas.media_root import (
    MediaRootCreateIn,
    MediaRootListOut,
    MediaRootOut,
)
from setvault_core.services.storage import probe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/media-roots", tags=["admin"])


def _to_out(r: MediaRoot) -> MediaRootOut:
    return MediaRootOut(
        id=str(r.id), name=r.name, host_path=r.host_path, enabled=r.enabled,
        default_for_ingest=r.default_for_ingest, max_bytes=r.max_bytes,
        naming_template=r.naming_template, last_health_status=r.last_health_status,
    )


@router.get("", response_model=MediaRootListOut)
async def list_roots(
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    rows = (
        await session.execute(select(MediaRoot).order_by(MediaRoot.created_at))
    ).scalars().all()
    return MediaRootListOut(items=[_to_out(r) for r in rows])


@router.post("", response_model=MediaRootOut, status_code=201)
async def create_root(
    body: MediaRootCreateIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    health = probe(body.host_path)
    if body.default_for_ingest:
        for existing in (await session.execute(
            select(MediaRoot).where(MediaRoot.default_for_ingest.is_(True))
        )).scalars():
            existing.default_for_ingest = False
    row = MediaRoot(
        name=body.name, host_path=body.host_path, enabled=True,
        default_for_ingest=body.default_for_ingest, max_bytes=body.max_bytes,
        naming_template=body.naming_template, last_health_status=health,
        last_health_check_at=datetime.now(UTC),
    )
    session.add(row)
    await session.commit()
    return _to_out(row)


@router.delete("/{root_id}", status_code=204)
async def delete_root(
    root_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    row = await session.get(MediaRoot, root_id)
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    # Phase 2 keeps this simple: refuse delete if any LiveSet still references the root.
    from setvault_core.models.catalog import LiveSet
    in_use = (await session.execute(
        select(LiveSet.id).where(LiveSet.media_root_id == row.id).limit(1)
    )).first()
    if in_use is not None:
        raise HTTPException(
            status_code=409,
            detail="root has sets — move or delete them first",
        )
    await session.delete(row)
    await session.commit()
