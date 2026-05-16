from __future__ import annotations

from pydantic import BaseModel, Field

from setvault_core.services.storage import HealthStatus  # re-exported for schema consumers

__all__ = [
    "HealthStatus",
    "MediaRootCreateIn",
    "MediaRootListOut",
    "MediaRootOut",
]


class MediaRootCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    host_path: str = Field(min_length=1, max_length=2048)
    default_for_ingest: bool = False
    max_bytes: int | None = None
    naming_template: str | None = None


class MediaRootOut(BaseModel):
    id: str
    name: str
    host_path: str
    enabled: bool
    default_for_ingest: bool
    max_bytes: int | None
    naming_template: str | None
    last_health_status: HealthStatus


class MediaRootListOut(BaseModel):
    items: list[MediaRootOut]
