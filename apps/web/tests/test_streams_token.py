"""Signature-based stream authorization tests.

The RSS-scope ApiToken is *not* a stream credential. Stream access is
gated by short-TTL HMAC signatures (`?sig=&exp=`) embedded in RSS
enclosure URLs.
"""
from __future__ import annotations

import time
import uuid as uuidmod
from pathlib import Path

import pytest


async def _seed_streamable(seeded_live_set: dict) -> None:
    """Give the seeded LiveSet a streaming_path + a placeholder file so the
    endpoint reaches its auth gate instead of short-circuiting on 404.

    The negative-case tests (bogus sig, expired sig, wrong slug, etc.) only
    exercise the auth path if the row + file exist; otherwise the upstream
    ``streaming_path is None`` check returns 404 first.
    """
    from setvault_core.db import session_factory
    from setvault_core.models.catalog import LiveSet, MediaRoot
    from sqlalchemy import select

    async with session_factory()() as s:
        live = await s.get(LiveSet, uuidmod.UUID(seeded_live_set["id"]))
        if live.streaming_path is None:
            live.streaming_path = "stream/seed.opus"
            await s.commit()
        mr = (await s.execute(
            select(MediaRoot).where(MediaRoot.default_for_ingest.is_(True)),
        )).scalar_one()
        host_path = mr.host_path

    target = Path(host_path) / "stream" / "seed.opus"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(b"\x00\x00")


@pytest.mark.asyncio
async def test_stream_with_valid_sig_no_cookie(client, seeded_live_set):
    """A request with valid ?sig=&exp= streams audio without a cookie."""
    from setvault_core.services.signed_urls import sign_stream_url
    from setvault_web.config import get_settings

    await _seed_streamable(seeded_live_set)
    sig, exp = sign_stream_url(
        secret_key=get_settings().secret_key, slug=seeded_live_set["slug"],
    )

    client.cookies.clear()
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?sig={sig}&exp={exp}",
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_stream_without_cookie_or_sig_returns_401(client, seeded_live_set):
    """Anonymous access fails when embed_allowed is False and no sig is given."""
    await _seed_streamable(seeded_live_set)
    client.cookies.clear()
    r = await client.get(f"/api/sets/{seeded_live_set['slug']}/stream")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_bogus_sig_returns_401(client, seeded_live_set):
    """A wrong signature must not authorize."""
    await _seed_streamable(seeded_live_set)
    client.cookies.clear()
    future_exp = int(time.time()) + 3600
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?sig=deadbeef&exp={future_exp}",
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_expired_sig_returns_401(client, seeded_live_set):
    """A signature past its exp must not authorize, even if it was valid before."""
    from setvault_core.services.signed_urls import sign_stream_url
    from setvault_web.config import get_settings

    await _seed_streamable(seeded_live_set)
    past_exp = int(time.time()) - 60  # 1 minute ago
    sig, _ = sign_stream_url(
        secret_key=get_settings().secret_key,
        slug=seeded_live_set["slug"], exp=past_exp,
    )

    client.cookies.clear()
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?sig={sig}&exp={past_exp}",
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_sig_for_different_slug_returns_401(client, seeded_live_set):
    """A signature minted for slug A must not authorize access to slug B."""
    from setvault_core.services.signed_urls import sign_stream_url
    from setvault_web.config import get_settings

    await _seed_streamable(seeded_live_set)
    sig, exp = sign_stream_url(
        secret_key=get_settings().secret_key, slug="not-this-slug",
    )

    client.cookies.clear()
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?sig={sig}&exp={exp}",
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_rss_token_does_not_authorize_stream(
    client, seeded_admin, seeded_live_set,
):
    """The RSS-scope ApiToken used to authorize stream access; it must no longer.

    This is the key blast-radius narrowing: the long-lived token in a user's
    feed XML URL is *only* a feed-XML credential, not a stream credential.
    """
    from setvault_core.db import session_factory
    from setvault_core.services.api_tokens import mint_api_token

    await _seed_streamable(seeded_live_set)

    async with session_factory()() as s:
        _, plaintext = await mint_api_token(
            s, user_id=seeded_admin.id, name="rss", scopes=["rss"],
        )
        await s.commit()

    client.cookies.clear()
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?token={plaintext}",
    )
    assert r.status_code == 401
