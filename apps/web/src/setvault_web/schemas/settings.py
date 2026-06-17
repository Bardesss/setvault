from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsOut(BaseModel):
    """Editable app-wide settings backed by the ``SystemConfig`` singleton."""

    audit_retention_days: int
    monitors_allow_all_users: bool
    monitor_interval_seconds: int
    single_user_auto_login: bool


class SettingsIn(BaseModel):
    """Partial update — only the supplied fields are written.

    All fields optional so callers can patch a single toggle without echoing
    the rest of the config back.
    """

    audit_retention_days: int | None = Field(default=None, ge=0)
    monitors_allow_all_users: bool | None = None
    monitor_interval_seconds: int | None = Field(default=None, ge=60)
    single_user_auto_login: bool | None = None
