from __future__ import annotations

import secrets as _s
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from setvault_core.models.identity import EmailToken, User
from setvault_core.services.passwords import hash_password
from setvault_core.services.sessions import SESSION_COOKIE, SESSION_TTL, SessionSigner
from setvault_core.services.tokens import expires, generate_token, hash_token, now_utc
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.api.auth import UserOut
from setvault_web.config import Settings, get_settings
from setvault_web.deps import db_session, get_signer, require_admin
from setvault_web.middleware.csrf import CSRF_COOKIE
from setvault_web.rate_limit import enforce_auth_strict

router = APIRouter(prefix="/api/invites", tags=["invites"])


class InviteCreateIn(BaseModel):
    email: str  # str, not EmailStr — .test TLD is rejected by email-validator
    role: Literal["admin", "user"] = "user"


class InviteOut(BaseModel):
    id: str
    email: str
    role: str
    expires_at: datetime
    invite_link: str
    smtp_sent: bool


@router.post("", response_model=InviteOut, status_code=201)
async def create_invite(
    body: InviteCreateIn,
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[User, Depends(require_admin)],
):
    plaintext, digest = generate_token()
    token = EmailToken(
        email=body.email, kind="invite", token_hash=digest,
        payload={"role": body.role}, expires_at=expires(72),
    )
    session.add(token)
    await session.commit()
    smtp_sent = await _try_send_invite_email(session, body.email, plaintext, settings)
    # Derive base URL from the incoming request so tests and local dev use the correct origin.
    base = str(request.base_url).rstrip("/")
    return InviteOut(
        id=str(token.id), email=body.email, role=body.role,
        expires_at=token.expires_at, smtp_sent=smtp_sent,
        invite_link=f"{base}/invite/{plaintext}",
    )


async def _try_send_invite_email(session, email, plaintext, settings) -> bool:
    from redis import Redis
    from rq import Queue
    from setvault_core.models.system import NotificationConnector

    row = (await session.execute(
        select(NotificationConnector).where(
            NotificationConnector.kind == "smtp", NotificationConnector.enabled.is_(True),
        ).limit(1)
    )).scalar_one_or_none()
    if row is None:
        return False
    queue = Queue("default", connection=Redis.from_url(settings.redis_url))
    link = f"{settings.base_url}/invite/{plaintext}"
    queue.enqueue(
        "setvault_core.jobs.email.send_email_job",
        connector_id=str(row.id), to=email,
        subject="You've been invited to SetVault",
        text=f"Open this link to set your username and password:\n\n{link}\n",
    )
    return True


class InviteRedeemIn(BaseModel):
    username: str
    display_name: str
    password: str


class LoginOut(BaseModel):
    user: UserOut


@router.post(
    "/{token}/redeem",
    response_model=LoginOut,
    dependencies=[Depends(enforce_auth_strict)],
)
async def redeem(
    token: str,
    body: InviteRedeemIn,
    response: Response,
    session: Annotated[AsyncSession, Depends(db_session)],
    signer: Annotated[SessionSigner, Depends(get_signer)],
):
    digest = hash_token(token)
    row = (await session.execute(
        select(EmailToken).where(EmailToken.token_hash == digest, EmailToken.kind == "invite")
    )).scalar_one_or_none()
    if row is None or row.used_at is not None or (row.expires_at and row.expires_at < now_utc()):
        raise HTTPException(status_code=410, detail="invite invalid or expired")
    if (await session.execute(
        select(User).where((User.email == row.email) | (User.username == body.username))
    )).scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="email or username already in use")
    user = User(
        email=row.email, username=body.username, display_name=body.display_name,
        password_hash=hash_password(body.password), role=row.payload.get("role", "user"),
        email_verified_at=datetime.now(UTC),
    )
    session.add(user)
    row.used_at = datetime.now(UTC)
    await session.commit()

    cookie = signer.issue(str(user.id))
    response.set_cookie(SESSION_COOKIE, cookie, httponly=True, secure=True, samesite="lax",
                        max_age=int(SESSION_TTL.total_seconds()), path="/")
    response.set_cookie(CSRF_COOKIE, _s.token_urlsafe(32), httponly=False, secure=True,
                        samesite="lax", path="/")
    return LoginOut(user=UserOut.from_model(user))
