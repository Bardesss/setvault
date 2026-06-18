import os
import uuid
from unittest.mock import patch

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist


@pytest.fixture
async def an_artist(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        a = Artist(name="Enrichable", slug=f"en-{uuid.uuid4().hex[:6]}")
        s.add(a)
        await s.commit()
        yield a.slug


@pytest.mark.asyncio
async def test_enrich_endpoint_returns_written(authed_admin_client, an_artist):
    async def fake_enrich(session, *, artist, providers):
        artist.bio = "x"
        return ["bio"]

    with patch("setvault_web.api.catalog.enrich_artist_entity", side_effect=fake_enrich), \
         patch("setvault_web.api.catalog.select_providers_for_capability", return_value=[object()]):
        r = await authed_admin_client.post(f"/api/catalog/artists/{an_artist}/enrich")
    assert r.status_code == 200
    assert r.json()["written"] == ["bio"]


@pytest.mark.asyncio
async def test_enrich_requires_auth(client, an_artist):
    # enrich is member-level (current_user); an anonymous caller must be rejected
    r = await client.post(f"/api/catalog/artists/{an_artist}/enrich")
    assert r.status_code in (401, 403)
