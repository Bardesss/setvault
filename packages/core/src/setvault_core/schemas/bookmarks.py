from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BookmarkOut(BaseModel):
    id: str
    live_set_id: str
    live_set_slug: str | None = None
    live_set_title: str | None = None
    position_seconds: int | None = None
    label: str | None = None
    created_at: datetime


class BookmarkCreateIn(BaseModel):
    position_seconds: int | None = Field(default=None, ge=0)
    label: str | None = Field(default=None, max_length=255)


class BookmarksListOut(BaseModel):
    items: list[BookmarkOut]
