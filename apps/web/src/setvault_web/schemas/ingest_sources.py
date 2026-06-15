from __future__ import annotations

from pydantic import BaseModel, Field


class SourceSearchIn(BaseModel):
    q: str
    source: str = "youtube"
    limit: int = Field(20, ge=1, le=50)


class CandidateOut(BaseModel):
    source_kind: str
    external_id: str
    title: str
    uploader: str | None
    duration_seconds: int | None
    thumbnail_url: str | None
    webpage_url: str
    already_in_library: bool


class SourceSearchOut(BaseModel):
    items: list[CandidateOut]


class SourceStateOut(BaseModel):
    kind: str
    name: str
    enabled: bool
    state: str
    consecutive_failures: int
    last_error: str | None


class SourceStatesOut(BaseModel):
    items: list[SourceStateOut]


class SetEnabledIn(BaseModel):
    enabled: bool
