from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class InAppNotificationOut(BaseModel):
    id: str
    kind: str
    subject_type: str
    subject_id: str
    payload: dict
    read_at: datetime | None = None
    created_at: datetime


class NotificationsListOut(BaseModel):
    items: list[InAppNotificationOut]
    unread_count: int
