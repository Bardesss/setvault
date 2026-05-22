import json
from pathlib import Path

import pytest
import respx
from httpx import Response
from setvault_providers.base import TrackRef
from setvault_providers.discogs import DiscogsProvider

FIXTURE = (
    Path(__file__).parents[3]
    / "apps" / "web" / "tests" / "fixtures" / "providers" / "discogs_release_search.json"
)


@pytest.mark.asyncio
async def test_enrich_track_returns_year_and_label():
    p = DiscogsProvider(token="t0k3n")
    payload = json.loads(FIXTURE.read_text())
    with respx.mock(assert_all_called=True) as mock:
        mock.get(host="api.discogs.com").mock(return_value=Response(200, json=payload))
        result = await p.enrich_track(TrackRef(title="Xtal", primary_artist_name="Aphex Twin"))
    assert result is not None
    assert result.fields["year"].value == 1992
    assert result.fields["label"].value == "R&S Records"
