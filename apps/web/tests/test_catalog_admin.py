import os
import uuid
from datetime import UTC, datetime

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


@pytest.fixture
async def merged_artists(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        survivor = Artist(name="Survivor Artist", slug=f"survivor-{uuid.uuid4().hex[:6]}")
        s.add(survivor)
        await s.flush()
        loser = Artist(
            name="Loser Artist",
            slug=f"loser-{uuid.uuid4().hex[:6]}",
            merged_into_id=survivor.id,
            merged_at=datetime.now(UTC),
        )
        unrelated = Artist(name="Unrelated Artist", slug=f"unrelated-{uuid.uuid4().hex[:6]}")
        s.add_all([loser, unrelated])
        await s.commit()
        yield {"survivor_name": survivor.name, "loser_name": loser.name}


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


@pytest.mark.asyncio
async def test_admin_merged_requires_admin(client):
    r = await client.get("/api/admin/catalog/artists/merged")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_admin_merged_lists_tombstoned(authed_admin_client, merged_artists):
    r = await authed_admin_client.get("/api/admin/catalog/artists/merged")
    assert r.status_code == 200
    items = r.json()["items"]
    names = {item["name"] for item in items}
    # The tombstoned loser must appear with the survivor's name
    assert merged_artists["loser_name"] in names
    loser_item = next(i for i in items if i["name"] == merged_artists["loser_name"])
    assert loser_item["survivor_name"] == merged_artists["survivor_name"]
    # The live survivor and unrelated artist must NOT appear
    assert merged_artists["survivor_name"] not in names
    assert "Unrelated Artist" not in names
