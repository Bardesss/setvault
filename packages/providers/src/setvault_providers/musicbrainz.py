from __future__ import annotations

from typing import ClassVar
from urllib.parse import quote_plus

import httpx

from setvault_providers.base import (
    Capability,
    FieldValue,
    ProviderError,
    ProviderRateLimited,
    ProviderResult,
    TrackRef,
)


class MusicBrainzProvider:
    kind = "musicbrainz"
    capabilities: ClassVar[set[Capability]] = {
        Capability.ENRICH_TRACK, Capability.ENRICH_RELEASE,
        Capability.ENRICH_ARTIST, Capability.LOOKUP_BY_ISRC,
    }

    def __init__(self, user_agent: str, base_url: str = "https://musicbrainz.org/ws/2"):
        if not user_agent:
            raise ValueError("MusicBrainz requires a user_agent per their ToS")
        self.user_agent = user_agent
        self.base_url = base_url

    async def _get(self, path: str, params: dict) -> dict:
        async with httpx.AsyncClient(
            timeout=15.0, headers={"User-Agent": self.user_agent}
        ) as c:
            r = await c.get(f"{self.base_url}/{path}", params={**params, "fmt": "json"})
        if r.status_code == 429:
            raise ProviderRateLimited("musicbrainz 429")
        if r.status_code != 200:
            raise ProviderError(f"musicbrainz {r.status_code}")
        return r.json()

    async def enrich_track(self, track: TrackRef) -> ProviderResult | None:
        if not track.title:
            return None
        q = f'recording:"{track.title}"'
        if track.primary_artist_name:
            q += f' AND artist:"{track.primary_artist_name}"'
        data = await self._get("recording", {"query": q, "limit": "1"})
        recs = data.get("recordings") or []
        if not recs:
            return None
        rec = recs[0]
        fields: dict[str, FieldValue] = {}
        if rec.get("isrcs"):
            fields["isrc"] = FieldValue(value=rec["isrcs"][0], confidence=0.9)
        rel = (rec.get("releases") or [{}])[0]
        if rel.get("date"):
            try:
                fields["year"] = FieldValue(value=int(rel["date"][:4]), confidence=0.85)
            except ValueError:
                pass
        if rec.get("title"):
            fields["title"] = FieldValue(value=rec["title"], confidence=0.95)
        if rec.get("artist-credit"):
            ac = rec["artist-credit"][0].get("artist", {})
            if ac.get("name"):
                fields["primary_artist"] = FieldValue(value=ac["name"], confidence=0.95)
        return ProviderResult(kind=self.kind, fields=fields, raw_response=data)

    async def enrich_artist(self, artist):
        return None

    async def enrich_release(self, release):
        return None

    async def lookup_by_isrc(self, isrc: str) -> TrackRef | None:
        data = await self._get(f"isrc/{quote_plus(isrc)}", {"inc": "artist-credits"})
        recs = data.get("recordings") or []
        if not recs:
            return None
        rec = recs[0]
        artist = (rec.get("artist-credit") or [{}])[0].get("artist", {}).get("name")
        return TrackRef(title=rec.get("title"), primary_artist_name=artist,
                        external_ids={"musicbrainz": rec.get("id", "")})

    async def fingerprint(self, *_args, **_kwargs):
        return []
