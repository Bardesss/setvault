from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PrivateNoteOut(BaseModel):
    body_md: str
    body_html: str
    updated_at: datetime | None = None


class PrivateNoteUpsertIn(BaseModel):
    body_md: str = Field(max_length=20_000)
