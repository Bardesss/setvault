import pytest
from setvault_core.services.enrichment import enrich_fields_in_memory
from setvault_providers.base import Capability, FieldValue, ProviderResult


class StubProvider:
    def __init__(self, kind, fields):
        self.kind = kind
        self.capabilities = {Capability.ENRICH_TRACK}
        self._fields = fields

    async def enrich_track(self, track):
        return ProviderResult(
            kind=self.kind,
            fields={k: FieldValue(value=v, confidence=0.9) for k, v in self._fields.items()},
            raw_response={},
        )

    async def enrich_artist(self, *a, **k):
        return None

    async def enrich_release(self, *a, **k):
        return None

    async def lookup_by_isrc(self, *a, **k):
        return None

    async def fingerprint(self, *a, **k):
        return []


@pytest.mark.asyncio
async def test_priority_walk_picks_first_provider():
    p1 = StubProvider("musicbrainz", {"isrc": "GB123", "year": 1992})
    p2 = StubProvider("discogs", {"year": 1995, "label": "RS"})
    fields = await enrich_fields_in_memory(
        providers=[p1, p2],
        track_ref_kwargs={"title": "Xtal", "primary_artist_name": "Aphex Twin"},
        field_priority={"year": ["discogs", "musicbrainz"]},
        locked_fields=set(),
    )
    assert fields["isrc"]["value"] == "GB123"
    assert fields["year"]["value"] == 1995
    assert fields["label"]["value"] == "RS"


@pytest.mark.asyncio
async def test_locked_fields_skipped():
    p = StubProvider("musicbrainz", {"year": 1992, "title": "Should not apply"})
    fields = await enrich_fields_in_memory(
        providers=[p],
        track_ref_kwargs={"title": "Existing"},
        field_priority={},
        locked_fields={"title"},
    )
    assert "title" not in fields
    assert fields["year"]["value"] == 1992
