import pytest


@pytest.mark.asyncio
async def test_bulk_resolve_returns_per_entry_candidates(authed_admin_client, seeded_live_set):
    await authed_admin_client.put("/api/admin/providers/musicbrainz", json={
        "name": "MB", "config": {"user_agent": "SetVault/test"},
    })
    slug = seeded_live_set["slug"]
    for i in range(3):
        await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries",
            json={"start_seconds": i * 60, "raw_label": f"A{i} - B{i}"},
        )
    r = await authed_admin_client.post(f"/api/sets/{slug}/tracklist/bulk-resolve")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "results" in body
    assert len(body["results"]) == 3
    for row in body["results"]:
        assert "entry_id" in row
        assert "candidates" in row
