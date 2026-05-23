from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from setvault_core.models.enrichment import ProviderConfig
from setvault_core.schemas.enrichment import ProviderConfigOut, ProviderConfigUpsertIn
from setvault_core.services.enrichment import encrypt_config, select_providers_for_capability
from setvault_providers.base import Capability, TrackRef
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import get_settings
from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/admin/providers", tags=["admin-providers"])

ProviderKind = Literal["musicbrainz", "discogs", "acoustid"]


def _to_out(p: ProviderConfig) -> ProviderConfigOut:
    return ProviderConfigOut(
        id=str(p.id),
        provider_kind=p.provider_kind,
        name=p.name,
        enabled=p.enabled,
        priority=p.priority,
        field_priority=p.field_priority or {},
    )


class ProvidersListOut(BaseModel):
    items: list[ProviderConfigOut]


@router.get("", response_model=ProvidersListOut)
async def list_providers(
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    rows = (await session.execute(
        select(ProviderConfig).order_by(ProviderConfig.priority)
    )).scalars().all()
    return ProvidersListOut(items=[_to_out(p) for p in rows])


@router.put("/{provider_kind}", response_model=ProviderConfigOut)
async def upsert_provider(
    provider_kind: ProviderKind,
    body: ProviderConfigUpsertIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    existing = (await session.execute(
        select(ProviderConfig).where(ProviderConfig.provider_kind == provider_kind)
    )).scalar_one_or_none()
    if existing is None:
        existing = ProviderConfig(provider_kind=provider_kind, name=body.name or provider_kind)
        session.add(existing)
    if body.name is not None:
        existing.name = body.name
    if body.enabled is not None:
        existing.enabled = body.enabled
    if body.priority is not None:
        existing.priority = body.priority
    if body.config is not None:
        existing.encrypted_config = encrypt_config(body.config, get_settings().secret_key)
    if body.field_priority is not None:
        existing.field_priority = body.field_priority
    await session.commit()
    return _to_out(existing)


@router.post("/{provider_kind}/test", response_model=dict)
async def test_provider(
    provider_kind: ProviderKind,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    cfg = (await session.execute(
        select(ProviderConfig).where(ProviderConfig.provider_kind == provider_kind)
    )).scalar_one_or_none()
    if cfg is None or not cfg.enabled:
        raise HTTPException(status_code=404, detail="provider not configured")
    cap = Capability.FINGERPRINT if provider_kind == "acoustid" else Capability.ENRICH_TRACK
    insts = select_providers_for_capability(
        [cfg], cap, secret_key=get_settings().secret_key
    )
    if not insts:
        return {"ok": False, "error": "cannot instantiate"}
    p = insts[0]
    try:
        if cap == Capability.ENRICH_TRACK:
            r = await p.enrich_track(TrackRef(title="Xtal", primary_artist_name="Aphex Twin"))
            return {"ok": True, "found_fields": list((r.fields if r else {}).keys())}
        return {"ok": True, "note": "fingerprint test skipped (no audio path)"}
    except Exception as e:  # surface any provider/network failure as a test result
        return {"ok": False, "error": str(e)[:200]}
