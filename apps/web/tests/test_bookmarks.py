import pytest


@pytest.mark.asyncio
async def test_create_set_level_bookmark(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    r = await authed_admin_client.post(f"/api/sets/{slug}/bookmarks", json={})
    assert r.status_code == 201
    body = r.json()
    assert body["position_seconds"] is None


@pytest.mark.asyncio
async def test_create_timestamped_bookmark(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    r = await authed_admin_client.post(f"/api/sets/{slug}/bookmarks",
                                         json={"position_seconds": 137, "label": "drop"})
    assert r.status_code == 201
    assert r.json()["label"] == "drop"


@pytest.mark.asyncio
async def test_my_bookmarks_returns_all(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    await authed_admin_client.post(f"/api/sets/{slug}/bookmarks", json={})
    await authed_admin_client.post(f"/api/sets/{slug}/bookmarks",
                                     json={"position_seconds": 60})
    r = await authed_admin_client.get("/api/me/bookmarks")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 2
