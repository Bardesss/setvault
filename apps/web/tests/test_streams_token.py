from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_stream_with_valid_rss_token_no_cookie(client, seeded_admin, seeded_live_set, tmp_path):
    """A request with ?token=<rss-scope token> and no session cookie streams audio."""
    from setvault_core.db import session_factory
    from setvault_core.models.catalog import LiveSet
    from setvault_core.services.api_tokens import mint_api_token

    # Mint the rss token + give the seeded set a streamable file on disk
    async with session_factory()() as s:
        _, plaintext = await mint_api_token(
            s, user_id=seeded_admin.id, name="stream", scopes=["rss"],
        )
        live = await s.get(LiveSet, __import__("uuid").UUID(seeded_live_set["id"]))
        live.streaming_path = "stream/seed.opus"
        await s.commit()

    # Write a placeholder file so FileResponse can serve it
    from setvault_core.models.catalog import MediaRoot
    from sqlalchemy import select
    async with session_factory()() as s:
        mr = (await s.execute(select(MediaRoot).where(MediaRoot.default_for_ingest.is_(True)))).scalar_one()
        path = mr.host_path
    target = __import__("pathlib").Path(path) / "stream" / "seed.opus"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\x00")

    # No cookie at all on this client
    client.cookies.clear()
    r = await client.get(
        f"/api/sets/{seeded_live_set['slug']}/stream?token={plaintext}",
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_stream_without_cookie_or_token_returns_401(client, seeded_live_set):
    """Anonymous access fails when embed_allowed is False and no token is given."""
    client.cookies.clear()
    r = await client.get(f"/api/sets/{seeded_live_set['slug']}/stream")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_stream_with_bogus_token_returns_401(client, seeded_live_set):
    """An unknown token must not authorize."""
    client.cookies.clear()
    r = await client.get(f"/api/sets/{seeded_live_set['slug']}/stream?token=deadbeef")
    assert r.status_code == 401
