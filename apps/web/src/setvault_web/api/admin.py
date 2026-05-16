from __future__ import annotations

import os
from typing import Annotated

from fastapi import APIRouter, Depends
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from setvault_core.models.system import AuditEvent
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web import __version__
from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

_REDACT_SUFFIXES = ("_KEY", "_SECRET", "_TOKEN", "_PASSWORD", "_HOOK_SECRET")


@router.get("/audit")
async def audit_list(
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
    action: str | None = None,
):
    stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(500)
    if action:
        stmt = stmt.where(AuditEvent.action == action)
    rows = (await session.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": str(e.id),
                "action": e.action,
                "actor_kind": e.actor_kind,
                "actor_user_id": str(e.actor_user_id) if e.actor_user_id else None,
                "target_type": e.target_type,
                "target_id": e.target_id,
                "before": e.before,
                "after": e.after,
                "created_at": e.created_at.isoformat(),
            }
            for e in rows
        ]
    }


@router.get("/system")
async def system_info(
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    user_count = (await session.execute(select(func.count(User.id)))).scalar_one()
    set_count = (await session.execute(
        select(func.count(LiveSet.id)).where(LiveSet.deleted_at.is_(None))
    )).scalar_one()
    env = {
        k: v
        for k, v in os.environ.items()
        if not any(k.upper().endswith(suf) for suf in _REDACT_SUFFIXES)
        and "PASS" not in k.upper()
        and "TOKEN" not in k.upper()
    }
    return {
        "version": __version__,
        "user_count": int(user_count),
        "set_count": int(set_count),
        "env": env,
    }
