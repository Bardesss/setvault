from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.identity import User
from setvault_core.services.audit import log as audit_log
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session, require_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/{user_id}/disable", status_code=204)
async def disable_user(
    user_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(db_session)],
    admin: Annotated[User, Depends(current_user)],
    _: Annotated[object, Depends(require_admin)],
):
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="not found")
    target.disabled_at = datetime.now(UTC)
    await audit_log(
        session,
        actor_user_id=admin.id,
        action="user.disabled",
        target_type="User",
        target_id=str(target.id),
    )
    await session.commit()
