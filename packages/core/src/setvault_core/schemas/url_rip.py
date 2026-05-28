from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RipSubmitIn(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class RipJobOut(BaseModel):
    id: str
    live_set_id: str | None
    live_set_slug: str | None
    source_url: str
    source_external_id: str | None
    source_platform: str | None
    status: str
    progress_pct: int
    message: str | None
    error_text: str | None
    probed_metadata: dict
    ytdlp_version: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class RipJobsListOut(BaseModel):
    items: list[RipJobOut]
