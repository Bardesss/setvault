from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from setvault_core.models.base import Base


class SystemConfig(Base):
    """Singleton row holding app-wide runtime settings.

    Enforced by the migration's ``CHECK (singleton = true)`` constraint, so
    the table always contains exactly one row. Callers read via
    ``services.system_config.get_config(session)``.
    """

    __tablename__ = "system_config"

    singleton: Mapped[bool] = mapped_column(Boolean, primary_key=True, default=True)
    latest_release_version: Mapped[str | None] = mapped_column(
        String(40), nullable=True,
    )
    latest_release_url: Mapped[str | None] = mapped_column(
        String(2048), nullable=True,
    )
    latest_release_etag: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )
    latest_release_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    audit_retention_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=90,
    )
    monitors_allow_all_users: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
    monitor_interval_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3600,
    )
    # When true AND exactly one active user exists, the app auto-authenticates
    # as that sole user (skips the login page). For trusted local/VPN use only;
    # the admin toggle is gated to the single-user case (see api/admin.py).
    single_user_auto_login: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
