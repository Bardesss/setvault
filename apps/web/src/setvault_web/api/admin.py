from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from setvault_core.models.system import AuditEvent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


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
