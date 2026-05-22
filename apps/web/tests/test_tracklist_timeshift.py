import pytest


@pytest.mark.asyncio
async def test_time_shift_shifts_entries_after_threshold(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    for i, sec in enumerate([0, 60, 120, 180]):
        await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries",
            json={"start_seconds": sec, "raw_label": f"t{i}"},
        )
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/time-shift",
        json={"after_seconds": 30, "delta_seconds": 27},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["affected_count"] == 3
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    starts = [e["start_seconds"] for e in listing["entries"]]
    assert starts == [0, 87, 147, 207]


@pytest.mark.asyncio
async def test_time_shift_clamps_to_zero(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    for sec in [10, 20, 30]:
        await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries",
            json={"start_seconds": sec, "raw_label": "t"},
        )
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/time-shift",
        json={"after_seconds": 0, "delta_seconds": -100},
    )
    assert r.status_code == 200
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    assert all(e["start_seconds"] == 0 for e in listing["entries"])
