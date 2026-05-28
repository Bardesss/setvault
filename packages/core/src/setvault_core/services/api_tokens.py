"""Mint / resolve / revoke ApiToken rows.

Tokens are random URL-safe strings; only the sha256 digest is stored.
Plaintext is returned exactly once at mint time. Each token carries one or
more scopes (e.g. "rss") that callers check before accepting it.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.api_token import ApiToken
from setvault_core.services.tokens import generate_token, hash_token


async def mint_api_token(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    name: str,
    scopes: list[str],
) -> tuple[ApiToken, str]:
    """Create a new ApiToken. Returns (row, plaintext_token).

    The plaintext is *only* available here — after this call only the sha256
    digest survives, so the caller must hand the plaintext back to the user
    immediately and never persist it.
    """
    plaintext, digest = generate_token()
    row = ApiToken(
        user_id=user_id,
        name=name.strip() or "unnamed",
        token_hash=digest,
        scopes=list(scopes),
    )
    session.add(row)
    await session.flush()
    return row, plaintext


async def resolve_api_token(
    session: AsyncSession, *, token_plaintext: str, required_scope: str,
) -> ApiToken | None:
    """Look up a token by plaintext + required scope. Returns the row or None.

    None covers all failure modes (missing, revoked, wrong scope) — callers
    should treat them identically so the response never leaks which case
    matched.
    """
    if not token_plaintext:
        return None
    digest = hash_token(token_plaintext)
    row = (await session.execute(
        select(ApiToken).where(
            ApiToken.token_hash == digest,
            ApiToken.revoked_at.is_(None),
        )
    )).scalar_one_or_none()
    if row is None:
        return None
    if required_scope not in (row.scopes or []):
        return None
    return row


async def touch_last_used(session: AsyncSession, token: ApiToken) -> None:
    """Bump last_used_at; caller commits."""
    token.last_used_at = datetime.now(UTC)
    await session.flush()


async def revoke_api_token(
    session: AsyncSession, *, user_id: uuid.UUID, token_id: uuid.UUID,
) -> bool:
    """Soft-revoke. Returns True if revoked, False if not found / already revoked."""
    row = (await session.execute(
        select(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.user_id == user_id,
            ApiToken.revoked_at.is_(None),
        )
    )).scalar_one_or_none()
    if row is None:
        return False
    row.revoked_at = datetime.now(UTC)
    await session.flush()
    return True
