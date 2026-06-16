from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class MonitorCreate(BaseModel):
    kind: str  # query | entity
    query_text: str | None = None
    source_kind: str | None = None
    external_id: str | None = None
    per_poll_cap: int = 5

    @model_validator(mode="after")
    def _check(self) -> MonitorCreate:
        if self.kind == "query":
            if not (self.query_text and self.query_text.strip()):
                raise ValueError("query monitor requires query_text")
        elif self.kind == "entity":
            if not self.source_kind or not self.external_id:
                raise ValueError("entity monitor requires source_kind and external_id")
        else:
            raise ValueError("kind must be 'query' or 'entity'")
        return self


class MonitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    kind: str
    query_text: str | None
    source_kind: str | None
    external_id: str | None
    enabled: bool
    per_poll_cap: int
    last_checked_at: datetime | None
    created_at: datetime


class MonitorsListOut(BaseModel):
    items: list[MonitorOut]


class MonitorUpdate(BaseModel):
    enabled: bool


class DiscoveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    monitor_id: str
    source_kind: str
    external_id: str
    title: str
    uploader: str | None
    webpage_url: str
    duration_seconds: int | None
    thumbnail_url: str | None
    confidence: str
    status: str
    created_at: datetime


class DiscoveriesListOut(BaseModel):
    items: list[DiscoveryOut]
