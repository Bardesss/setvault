from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.db import session_factory
from setvault_core.models.identity import User
from setvault_core.services.sessions import SESSION_COOKIE, SessionSigner

from setvault_web.config import Settings, get_settings


def get_signer(settings: Annotated[Settings, Depends(get_settings)]) -> SessionSigner:
    return SessionSigner(settings.secret_key)


async def db_session() -> AsyncIterator[AsyncSession]:
    async with session_factory()() as s:
        yield s


async def current_user(
    session: Annotated[AsyncSession, Depends(db_session)],
    signer: Annotated[SessionSigner, Depends(get_signer)],
    session_cookie: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> User:
    if not session_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    data = signer.read(session_cookie)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid session")
    try:
        user_id = uuid.UUID(data.user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid session"
        ) from exc
    user = await session.get(User, user_id)
    if user is None or user.disabled_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user inactive")
    return user


async def require_admin(user: Annotated[User, Depends(current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin only")
    return user
