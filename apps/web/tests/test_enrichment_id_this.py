import json
from pathlib import Path

import pytest
import respx
from httpx import Response

LOOKUP_FIXTURE = Path(__file__).parent / "fixtures" / "providers" / "acoustid_lookup.json"


@pytest.mark.asyncio
async def test_id_this_returns_candidates(authed_admin_client, seeded_live_set, monkeypatch):
    await authed_admin_client.put("/api/admin/providers/acoustid", json={
        "name": "AID", "config": {"api_key": "k"},
    })
    slug = seeded_live_set["slug"]
    entry = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "x"},
    )).json()

    # The seeded LiveSet has no streaming_path by default; patch it in.
    from setvault_core.db import session_factory
    from setvault_core.models.catalog import LiveSet
    from sqlalchemy import select
    async with session_factory()() as s:
        live = (await s.execute(select(LiveSet).where(LiveSet.slug == slug))).scalar_one()
        live.streaming_path = "stream/x.opus"
        await s.commit()

    from setvault_providers.acoustid import AcoustIdProvider
    monkeypatch.setattr(AcoustIdProvider, "_extract_window",
                        lambda self, *a, **k: Path("/tmp/x.wav"))  # noqa: S108

    async def fake_fpcalc(self, path, length):
        return {"duration": 15, "fingerprint": "fakeprint"}

    monkeypatch.setattr(AcoustIdProvider, "_run_fpcalc", fake_fpcalc)

    payload = json.loads(LOOKUP_FIXTURE.read_text())
    with respx.mock(assert_all_called=True) as mock:
        mock.post(host="api.acoustid.org").mock(return_value=Response(200, json=payload))
        r = await authed_admin_client.post(
            f"/api/sets/{slug}/tracklist/entries/{entry['id']}/id-this",
        )
    assert r.status_code == 200, r.text
    cands = r.json()["candidates"]
    assert cands[0]["title"] == "Xtal"
    assert cands[0]["confidence"] == 0.93


@pytest.mark.asyncio
async def test_id_this_404_without_audio(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    entry = (await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries",
        json={"start_seconds": 0, "raw_label": "x"},
    )).json()
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/entries/{entry['id']}/id-this",
    )
    assert r.status_code == 404
