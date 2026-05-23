from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProviderConfigOut(BaseModel):
    id: str
    provider_kind: Literal["musicbrainz", "discogs", "acoustid"]
    name: str
    enabled: bool
    priority: int
    field_priority: dict[str, list[str]] = Field(default_factory=dict)


class ProviderConfigUpsertIn(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    priority: int | None = None
    config: dict | None = None  # plaintext, server encrypts before storage
    field_priority: dict[str, list[str]] | None = None


class ResolveCandidate(BaseModel):
    title: str
    artist_name: str
    confidence: float
    source_kind: str
    external_ids: dict[str, str] = Field(default_factory=dict)


class ResolveOut(BaseModel):
    entry_id: str
    candidates: list[ResolveCandidate]


class ResolveAcceptIn(BaseModel):
    title: str
    artist_name: str
    external_ids: dict[str, str] = Field(default_factory=dict)
    confirmed_via_acoustid: bool = False
