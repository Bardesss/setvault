from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from setvault_core.models.base import Base, TimestampMixin, UuidPkMixin


class IngestSourceState(Base, UuidPkMixin, TimestampMixin):
    """Per-source enable + health state machine. One row per source kind.

    state: healthy | degraded | auto_disabled | manually_disabled
    """

    __tablename__ = "ingest_source_state"

    kind: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    state: Mapped[str] = mapped_column(String(32), default="healthy", nullable=False)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rate_limit_max: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    rate_limit_window_seconds: Mapped[int] = mapped_column(
        Integer, default=60, nullable=False
    )
