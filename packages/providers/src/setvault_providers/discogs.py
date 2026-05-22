from __future__ import annotations

from typing import ClassVar

import httpx

from setvault_providers.base import (
    Capability,
    FieldValue,
    ProviderError,
    ProviderRateLimited,
    ProviderResult,
    TrackRef,
)


class DiscogsProvider:
    kind = "discogs"
    capabilities: ClassVar[set[Capability]] = {
        Capability.ENRICH_TRACK, Capability.ENRICH_RELEASE, Capability.ENRICH_ARTIST,
    }

    def __init__(self, token: str, base_url: str = "https://api.discogs.com"):
        if not token:
            raise ValueError("Discogs requires a personal access token")
        self.token = token
        self.base_url = base_url

    async def _get(self, path: str, params: dict) -> dict:
        headers = {"Authorization": f"Discogs token={self.token}",
                   "User-Agent": "SetVault/0.1"}
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as c:
            r = await c.get(f"{self.base_url}/{path}", params=params)
        if r.status_code == 429:
            raise ProviderRateLimited("discogs 429")
        if r.status_code != 200:
            raise ProviderError(f"discogs {r.status_code}")
        return r.json()

    async def enrich_track(self, track: TrackRef) -> ProviderResult | None:
        if not track.title:
            return None
        q = f"{track.primary_artist_name or ''} {track.title}".strip()
        data = await self._get("database/search", {"q": q, "type": "release", "per_page": 1})
        rs = data.get("results") or []
        if not rs:
            return None
        r = rs[0]
        fields: dict[str, FieldValue] = {}
        if r.get("year"):
            try:
                fields["year"] = FieldValue(value=int(r["year"]), confidence=0.8)
            except (TypeError, ValueError):
                pass
        if r.get("label"):
            label = r["label"][0] if isinstance(r["label"], list) else r["label"]
            fields["label"] = FieldValue(value=label, confidence=0.75)
        if r.get("catno"):
            fields["catalog_number"] = FieldValue(value=r["catno"], confidence=0.8)
        return ProviderResult(kind=self.kind, fields=fields, raw_response=data)

    async def enrich_artist(self, artist):
        return None

    async def enrich_release(self, release):
        return None

    async def lookup_by_isrc(self, isrc: str):
        return None

    async def fingerprint(self, *_args, **_kwargs):
        return []
