import pytest


@pytest.mark.asyncio
async def test_list_empty(authed_admin_client, seeded_live_set):
    r = await authed_admin_client.get(f"/api/sets/{seeded_live_set['slug']}/tracklist")
    assert r.status_code == 200, r.text
    assert r.json() == {"entries": []}


@pytest.mark.asyncio
async def test_create_entry(authed_admin_client, seeded_live_set):
    r = await authed_admin_client.post(
        f"/api/sets/{seeded_live_set['slug']}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "Aphex Twin - Xtal"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["position"] == 0
    assert body["start_seconds"] == 0
    assert body["raw_label"] == "Aphex Twin - Xtal"
    assert body["status"] == "raw"


@pytest.mark.asyncio
async def test_patch_entry(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    created = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "Old label"},
    )).json()
    r = await authed_admin_client.patch(
        f"/api/sets/{slug}/tracklist/entries/{created['id']}",
        json={"raw_label": "New label", "edit_notes": "fixed typo"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["raw_label"] == "New label"
    assert body["edit_notes"] == "fixed typo"


@pytest.mark.asyncio
async def test_delete_entry(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    created = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "x"},
    )).json()
    r = await authed_admin_client.delete(f"/api/sets/{slug}/tracklist/entries/{created['id']}")
    assert r.status_code == 204
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    assert listing["entries"] == []


@pytest.mark.asyncio
async def test_reorder(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    ids = []
    for i in range(3):
        r = await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries",
            json={"start_seconds": i * 60, "raw_label": f"t{i}"},
        )
        ids.append(r.json()["id"])
    r = await authed_admin_client.patch(
        f"/api/sets/{slug}/tracklist/entries/{ids[0]}/move",
        json={"after_position": 2},
    )
    assert r.status_code == 204
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    order = [e["id"] for e in listing["entries"]]
    assert order == [ids[1], ids[2], ids[0]]


@pytest.mark.asyncio
async def test_404_for_unknown_set(authed_admin_client):
    r = await authed_admin_client.get("/api/sets/no-such-set/tracklist")
    assert r.status_code == 404
