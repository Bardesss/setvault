from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.catalog import LiveSet
from setvault_core.models.enrichment import ProviderConfig
from setvault_core.models.identity import User
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.schemas.enrichment import ResolveAcceptIn, ResolveCandidate, ResolveOut
from setvault_core.services.enrichment import (
    accept_candidate,
    resolve_entry,
    select_providers_for_capability,
)
from setvault_providers.base import Capability
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import get_settings
from setvault_web.deps import current_user, db_session

router = APIRouter(prefix="/api/sets", tags=["enrichment"])


async def _load_entry(
    session: AsyncSession, slug: str, entry_id: str
) -> tuple[LiveSet, TracklistEntry]:
    live = (await session.execute(
        select(LiveSet).where(LiveSet.slug == slug, LiveSet.deleted_at.is_(None))
    )).scalar_one_or_none()
    if live is None:
        raise HTTPException(status_code=404, detail="set not found")
    entry = (await session.execute(
        select(TracklistEntry).where(
            TracklistEntry.id == uuid.UUID(entry_id),
            TracklistEntry.live_set_id == live.id,
        )
    )).scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="entry not found")
    return live, entry


async def _enabled_configs(session: AsyncSession) -> list[ProviderConfig]:
    return list((await session.execute(
        select(ProviderConfig).where(ProviderConfig.enabled.is_(True))
        .order_by(ProviderConfig.priority)
    )).scalars().all())


def _field_priority_from(configs: list[ProviderConfig]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for cfg in configs:
        for fname, order in (cfg.field_priority or {}).items():
            out[fname] = order
    return out


def _to_candidates(rows: list[dict]) -> list[ResolveCandidate]:
    return [
        ResolveCandidate(**{k: v for k, v in c.items() if not k.startswith("_")})
        for c in rows
    ]


@router.post("/{slug}/tracklist/entries/{entry_id}/resolve", response_model=ResolveOut)
async def resolve_one(
    slug: str,
    entry_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    _, entry = await _load_entry(session, slug, entry_id)
    configs = await _enabled_configs(session)
    providers = select_providers_for_capability(
        configs, Capability.ENRICH_TRACK, secret_key=get_settings().secret_key
    )
    field_priority = _field_priority_from(configs)
    cands = await resolve_entry(session, entry, providers, field_priority)
    await session.commit()
    return ResolveOut(entry_id=entry_id, candidates=_to_candidates(cands))


@router.post("/{slug}/tracklist/entries/{entry_id}/resolve/accept")
async def resolve_accept(
    slug: str,
    entry_id: str,
    body: ResolveAcceptIn,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(db_session)],
):
    _, entry = await _load_entry(session, slug, entry_id)
    configs = await _enabled_configs(session)
    providers = select_providers_for_capability(
        configs, Capability.ENRICH_TRACK, secret_key=get_settings().secret_key
    )
    field_priority = _field_priority_from(configs)
    track = await accept_candidate(
        session, entry,
        title=body.title, artist_name=body.artist_name,
        external_ids=body.external_ids,
        confirmed_via_acoustid=body.confirmed_via_acoustid,
        field_priority=field_priority, providers=providers,
    )
    await session.commit()
    return {"track_id": str(track.id), "status": entry.status}
