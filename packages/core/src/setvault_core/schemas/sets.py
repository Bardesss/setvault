from __future__ import annotations

from datetime import date as _date
from typing import Literal

from pydantic import BaseModel

from setvault_core.schemas.catalog import PartyOut, VenueOut

SetType = Literal["opener", "closer", "b2b", "headline", "warmup", "unknown"]


class SetArtistOut(BaseModel):
    id: str
    name: str
    slug: str
    role: str


class SetSummaryOut(BaseModel):
    id: str
    slug: str
    title: str
    date: _date | None
    duration_seconds: int | None
    set_type: SetType
    status: str
    artists: list[SetArtistOut]
    tags: list[str]


class SetDetailOut(SetSummaryOut):
    party: PartyOut | None
    venue: VenueOut | None
    description: str | None
    audio_stream_url: str
    waveform_url: str | None
    normalized_lufs: float | None
    embed_allowed: bool


class SetListOut(BaseModel):
    items: list[SetSummaryOut]
    total: int


class SetPatchIn(BaseModel):
    title: str | None = None
    date: _date | None = None
    set_type: SetType | None = None
    party_id: str | None = None
    venue_id: str | None = None
    description: str | None = None
    artist_ids: list[str] | None = None
    tag_names: list[str] | None = None
