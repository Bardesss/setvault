import pytest
import respx
from httpx import Response


@pytest.mark.asyncio
async def test_resolve_returns_candidates(authed_admin_client, seeded_live_set):
    await authed_admin_client.put("/api/admin/providers/musicbrainz", json={
        "name": "MB", "config": {"user_agent": "SetVault/test"},
    })
    slug = seeded_live_set["slug"]
    entry = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "Aphex Twin - Xtal"},
    )).json()
    payload = {"recordings": [{
        "id": "11111111-2222-3333-4444-555555555555",
        "title": "Xtal",
        "isrcs": ["GBARL0500001"],
        "artist-credit": [{"artist": {"name": "Aphex Twin"}}],
        "releases": [{"date": "1992-02-09"}],
    }]}
    with respx.mock(assert_all_called=False) as mock:
        mock.get(host="musicbrainz.org").mock(return_value=Response(200, json=payload))
        r = await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries/{entry['id']}/resolve",
        )
    assert r.status_code == 200, r.text
    cands = r.json()["candidates"]
    assert any(c["title"] == "Xtal" and c["artist_name"] == "Aphex Twin" for c in cands)


@pytest.mark.asyncio
async def test_resolve_accept_flips_status(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    entry = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "x - y"},
    )).json()
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries/{entry['id']}/resolve/accept",
        json={"title": "y", "artist_name": "x", "external_ids": {}},
    )
    assert r.status_code == 200
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    assert listing["entries"][0]["status"] == "resolved"
    assert listing["entries"][0]["track_id"] is not None
