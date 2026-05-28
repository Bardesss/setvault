from __future__ import annotations

from pydantic import BaseModel


class RssTokenCreateIn(BaseModel):
    name: str


class RssTokenOut(BaseModel):
    id: str
    name: str
    favorites_url: str
    recent_url: str
    everything_url: str
    created_at: str
    last_used_at: str | None


class RssTokenWithPlaintextOut(RssTokenOut):
    token: str  # plaintext — shown once at mint time


class RssTokensListOut(BaseModel):
    items: list[RssTokenOut]
