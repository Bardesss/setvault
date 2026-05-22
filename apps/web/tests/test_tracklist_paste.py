from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "tracklists" / "sample_paste.txt"


@pytest.mark.asyncio
async def test_paste_returns_parsed_entries(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    text = FIXTURE.read_text()
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/import",
        json={"kind": "paste", "payload": {"text": text}},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "succeeded"
    parsed = body["parsed"]
    assert len(parsed) == 3
    assert parsed[0]["start_seconds"] == 0
    assert parsed[0]["raw_label"] == "Aphex Twin - Xtal"
    assert parsed[1]["start_seconds"] == 225
    assert parsed[2]["raw_label"].startswith("Floating Points")


@pytest.mark.asyncio
async def test_paste_accept_materializes_entries(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    imp = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/import",
        json={"kind": "paste", "payload": {"text": "0:00 A - B\n5:00 C - D"}},
    )).json()
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/import/{imp['id']}/accept",
        json={"accepted_indexes": [0, 1]},
    )
    assert r.status_code == 200
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/tracklist")).json()
    assert len(listing["entries"]) == 2
    assert listing["entries"][0]["raw_label"] == "A - B"
