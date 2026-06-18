import os
import uuid
import uuid as _uuid
from datetime import UTC, datetime

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist


@pytest.fixture
async def tombstoned_artist(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        survivor = Artist(name="Keep", slug=f"keep-{uuid.uuid4().hex[:6]}")
        s.add(survivor)
        await s.flush()
        dead = Artist(name="Gone", slug=f"gone-{uuid.uuid4().hex[:6]}",
                      merged_into_id=survivor.id, merged_at=datetime.now(UTC))
        s.add(dead)
        await s.commit()
        yield dead.slug


@pytest.mark.asyncio
async def test_get_tombstoned_artist_404(authed_admin_client, tombstoned_artist):
    r = await authed_admin_client.get(f"/api/catalog/artists/{tombstoned_artist}")
    assert r.status_code == 404


@pytest.fixture
async def two_artists(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        a = Artist(name="Keep", slug=f"keep-{_uuid.uuid4().hex[:6]}")
        b = Artist(name="Dup", slug=f"dup-{_uuid.uuid4().hex[:6]}")
        s.add_all([a, b])
        await s.commit()
        yield {"survivor": str(a.id), "loser": str(b.id), "loser_slug": b.slug}


@pytest.mark.asyncio
async def test_merge_requires_admin(client, two_artists):
    r = await client.post(f"/api/catalog/artists/{two_artists['loser']}/merge",
                          json={"survivor_id": two_artists["survivor"]})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_merge_dry_run_does_not_mutate(authed_admin_client, two_artists):
    r = await authed_admin_client.post(
        f"/api/catalog/artists/{two_artists['loser']}/merge?dry_run=1",
        json={"survivor_id": two_artists["survivor"]},
    )
    assert r.status_code == 200 and "preview" in r.json()
    # loser still reachable (not tombstoned)
    show = await authed_admin_client.get(f"/api/catalog/artists/{two_artists['loser_slug']}")
    assert show.status_code == 200


@pytest.mark.asyncio
async def test_merge_then_unmerge(authed_admin_client, two_artists):
    m = await authed_admin_client.post(
        f"/api/catalog/artists/{two_artists['loser']}/merge",
        json={"survivor_id": two_artists["survivor"]},
    )
    assert m.status_code == 200
    gone = await authed_admin_client.get(f"/api/catalog/artists/{two_artists['loser_slug']}")
    assert gone.status_code == 404
    u = await authed_admin_client.post(f"/api/catalog/artists/{two_artists['loser']}/unmerge")
    assert u.status_code == 204
    back = await authed_admin_client.get(f"/api/catalog/artists/{two_artists['loser_slug']}")
    assert back.status_code == 200


@pytest.mark.asyncio
async def test_delete_unreferenced_ok_referenced_409(authed_admin_client, seeded_admin):
    from setvault_core.models.catalog import LiveSet, LiveSetArtist, MediaRoot
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        free = Artist(name="Free", slug=f"free-{_uuid.uuid4().hex[:6]}")
        used = Artist(name="Used", slug=f"used-{_uuid.uuid4().hex[:6]}")
        root = MediaRoot(name=f"r-{_uuid.uuid4().hex[:6]}", host_path="/srv/test-media")
        s.add_all([free, used, root])
        await s.flush()
        ls = LiveSet(slug=f"s-{_uuid.uuid4().hex[:8]}", title="t", media_root_id=root.id,
                     audio_path="a/b.flac", status="published", source_type="upload",
                     uploaded_by=seeded_admin.id)
        s.add(ls)
        await s.flush()
        s.add(LiveSetArtist(live_set_id=ls.id, artist_id=used.id))
        await s.commit()
        free_slug, used_slug = free.slug, used.slug

    ok = await authed_admin_client.delete(f"/api/catalog/artists/{free_slug}")
    assert ok.status_code == 204
    conflict = await authed_admin_client.delete(f"/api/catalog/artists/{used_slug}")
    assert conflict.status_code == 409
