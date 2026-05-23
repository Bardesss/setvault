import json
from pathlib import Path

import pytest
import respx
from httpx import Response
from setvault_providers.acoustid import AcoustIdProvider

LOOKUP_FIXTURE = (
    Path(__file__).parents[3]
    / "apps" / "web" / "tests" / "fixtures" / "providers" / "acoustid_lookup.json"
)


@pytest.mark.asyncio
async def test_fingerprint_returns_candidates(monkeypatch, tmp_path):
    p = AcoustIdProvider(api_key="k")
    # Throwaway window file: fpcalc is stubbed so it is never decoded; fingerprint()
    # unlinks it at the end, which is fine since it lives in pytest's tmp dir.
    window_file = tmp_path / "window.wav"
    window_file.write_bytes(b"\x00")

    async def fake_fpcalc(self, path, length):
        return {"duration": 15, "fingerprint": "fakeprint"}

    monkeypatch.setattr(AcoustIdProvider, "_run_fpcalc", fake_fpcalc)
    monkeypatch.setattr(AcoustIdProvider, "_extract_window",
                        lambda self, *a, **k: window_file)

    payload = json.loads(LOOKUP_FIXTURE.read_text())
    with respx.mock(assert_all_called=True) as mock:
        mock.post(host="api.acoustid.org").mock(return_value=Response(200, json=payload))
        cands = await p.fingerprint("dummy.flac", start_seconds=0, window_seconds=15)
    assert len(cands) == 1
    assert cands[0].title == "Xtal"
    assert cands[0].artist_name == "Aphex Twin"
    assert cands[0].confidence == 0.93
