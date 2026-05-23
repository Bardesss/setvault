from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from setvault_core.models.base import Base, TimestampMixin, UuidPkMixin


class ProviderConfig(Base, UuidPkMixin, TimestampMixin):
    __tablename__ = "provider_configs"
    provider_kind: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    encrypted_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    field_priority: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class ProviderResponse(Base, UuidPkMixin):
    __tablename__ = "provider_responses"
    provider_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    query_key: Mapped[str] = mapped_column(String(512), nullable=False)
    response: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


ResolveJobKind = Literal["bulk_resolve", "single_entry", "acoustid_id_this"]
ResolveJobStatus = Literal["queued", "running", "succeeded", "failed"]


class ResolveJob(Base, UuidPkMixin):
    __tablename__ = "resolve_jobs"
    live_set_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("live_sets.id", ondelete="CASCADE"), nullable=True
    )
    kind: Mapped[ResolveJobKind] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[ResolveJobStatus] = mapped_column(
        String(24), nullable=False, default="queued"
    )
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
