from __future__ import annotations

import secrets as _secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from setvault_core.models.identity import User
from setvault_core.services.passwords import verify_password
from setvault_core.services.sessions import SESSION_COOKIE, SESSION_TTL, SessionSigner
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session, get_signer
from setvault_web.middleware.csrf import CSRF_COOKIE
from setvault_web.rate_limit import enforce_auth_strict

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    display_name: str
    role: str

    @classmethod
    def from_model(cls, u: User) -> UserOut:
        return cls(id=str(u.id), email=u.email, username=u.username,
                   display_name=u.display_name, role=u.role)


class LoginOut(BaseModel):
    user: UserOut


@router.post("/login", response_model=LoginOut, dependencies=[Depends(enforce_auth_strict)])
async def login(
    body: LoginIn,
    response: Response,
    session: Annotated[AsyncSession, Depends(db_session)],
    signer: Annotated[SessionSigner, Depends(get_signer)],
):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if (
        user is None
        or not user.password_hash
        or not verify_password(body.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials",
        )
    if user.disabled_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="account disabled")
    cookie = signer.issue(str(user.id))
    response.set_cookie(
        SESSION_COOKIE, cookie,
        httponly=True, secure=True, samesite="lax",
        max_age=int(SESSION_TTL.total_seconds()), path="/",
    )
    response.set_cookie(
        CSRF_COOKIE, _secrets.token_urlsafe(32),
        httponly=False, secure=True, samesite="lax", path="/",
    )
    return LoginOut(user=UserOut.from_model(user))


@router.post("/logout", status_code=204)
async def logout(response: Response, _: Annotated[User, Depends(current_user)]):
    response.delete_cookie(
        SESSION_COOKIE, path="/", secure=True, httponly=True, samesite="lax",
    )


@router.get("/me", response_model=UserOut)
async def me(user: Annotated[User, Depends(current_user)]):
    return UserOut.from_model(user)
