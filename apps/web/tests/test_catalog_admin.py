import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist


@pytest.fixture
async def dup_artists(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        s.add_all([
            Artist(name="DJ X", slug=f"x-{uuid.uuid4().hex[:6]}"),
            Artist(name="dj x", slug=f"y-{uuid.uuid4().hex[:6]}"),
            Artist(name="Unique One", slug=f"z-{uuid.uuid4().hex[:6]}"),
        ])
        await s.commit()
    yield


@pytest.mark.asyncio
async def test_admin_list_requires_admin(client):
    r = await client.get("/api/admin/catalog/artists")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_admin_list_and_duplicates(authed_admin_client, dup_artists):
    lst = await authed_admin_client.get("/api/admin/catalog/artists")
    assert lst.status_code == 200
    assert len(lst.json()["items"]) >= 3

    dups = await authed_admin_client.get("/api/admin/catalog/artists/duplicates")
    assert dups.status_code == 200
    clusters = dups.json()["clusters"]
    assert any({"DJ X", "dj x"} == {m["name"] for m in c} for c in clusters)
