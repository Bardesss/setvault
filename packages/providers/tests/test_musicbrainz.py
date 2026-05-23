import json
from pathlib import Path

import pytest
import respx
from httpx import Response
from setvault_providers.base import TrackRef
from setvault_providers.musicbrainz import MusicBrainzProvider

FIXTURE = (
    Path(__file__).parents[3]
    / "apps" / "web" / "tests" / "fixtures" / "providers" / "mb_track_search.json"
)


@pytest.mark.asyncio
async def test_enrich_track_returns_isrc_and_year():
    p = MusicBrainzProvider(user_agent="SetVault/test (test@example.com)")
    payload = json.loads(FIXTURE.read_text())
    with respx.mock(assert_all_called=True) as mock:
        mock.get(host="musicbrainz.org").mock(return_value=Response(200, json=payload))
        result = await p.enrich_track(TrackRef(title="Xtal", primary_artist_name="Aphex Twin"))
    assert result is not None
    assert result.kind == "musicbrainz"
    assert result.fields["isrc"].value == "GBARL0500001"
    assert result.fields["year"].value == 1992
    assert result.raw_response == payload
