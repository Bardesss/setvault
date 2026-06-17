import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist, LiveSet, LiveSetArtist, MediaRoot


@pytest.fixture
async def artist_with_set(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        root = MediaRoot(name=f"r-{uuid.uuid4().hex[:6]}", host_path="/srv/test-media")
        s.add(root)
        await s.flush()
        artist = Artist(name="Mappable", slug=f"mappable-{uuid.uuid4().hex[:6]}")
        s.add(artist)
        await s.flush()
        ls = LiveSet(slug=f"s-{uuid.uuid4().hex[:8]}", title="A Live Set",
                     media_root_id=root.id, audio_path="a/b.flac", status="published",
                     source_type="upload", uploaded_by=seeded_admin.id)
        s.add(ls)
        await s.flush()
        s.add(LiveSetArtist(live_set_id=ls.id, artist_id=artist.id, position=0))
        await s.commit()
        yield {"slug": artist.slug, "set_title": "A Live Set"}


@pytest.mark.asyncio
async def test_sets_by_artist(authed_admin_client, artist_with_set):
    r = await authed_admin_client.get(f"/api/catalog/artists/{artist_with_set['slug']}/sets")
    assert r.status_code == 200
    titles = [i["title"] for i in r.json()["items"]]
    assert artist_with_set["set_title"] in titles


@pytest.mark.asyncio
async def test_sets_by_entity_unknown_slug_404(authed_admin_client):
    r = await authed_admin_client.get("/api/catalog/artists/no-such-artist/sets")
    assert r.status_code == 404


@pytest.fixture
async def an_artist(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        a = Artist(name="Edit Me", slug=f"edit-me-{uuid.uuid4().hex[:6]}", country="BE")
        s.add(a)
        await s.commit()
        yield a.slug


@pytest.mark.asyncio
async def test_member_can_edit_artist_fields_slug_unchanged(authed_admin_client, an_artist):
    r = await authed_admin_client.patch(
        f"/api/catalog/artists/{an_artist}", json={"country": "NL", "bio": "techno"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["country"] == "NL"
    assert body["bio"] == "techno"
    assert body["slug"] == an_artist  # slug is stable


@pytest.mark.asyncio
async def test_edit_requires_auth(client, an_artist):
    r = await client.patch(f"/api/catalog/artists/{an_artist}", json={"country": "NL"})
    assert r.status_code in (401, 403)  # CSRF middleware returns 403 before auth check


@pytest.mark.asyncio
async def test_edit_unknown_slug_404(authed_admin_client):
    r = await authed_admin_client.patch("/api/catalog/artists/nope", json={"country": "NL"})
    assert r.status_code == 404
