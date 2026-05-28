from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WatchFolderCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    host_path: str = Field(min_length=1, max_length=2048)
    target_media_root_id: str
    enabled: bool = True


class WatchFolderPatchIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None


class WatchFolderOut(BaseModel):
    id: str
    name: str
    host_path: str
    target_media_root_id: str
    enabled: bool
    last_event_at: datetime | None
    last_health_check_at: datetime | None
    last_health_status: str
    created_at: datetime


class WatchFolderListOut(BaseModel):
    items: list[WatchFolderOut]


class UnmatchedFileOut(BaseModel):
    id: str
    watch_folder_id: str
    file_path: str
    detected_at: datetime
    audio_info: dict
    resolution: str
    resolved_to_set_id: str | None
    error_text: str | None


class UnmatchedFileListOut(BaseModel):
    items: list[UnmatchedFileOut]


class UnmatchedResolveIn(BaseModel):
    """One of these branches MUST be selected:
      - action="link_to_set" + live_set_id
      - action="create_draft"
      - action="discard"
    """
    action: str  # link_to_set | create_draft | discard
    live_set_id: str | None = None
