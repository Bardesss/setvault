from __future__ import annotations

import asyncio
import os
import uuid

from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import LiveSet
from setvault_core.progress import ProgressEvent, publish
from setvault_core.services.activity import record


async def mark_ready(live_set_id: str) -> None:
    if "DATABASE_URL" in os.environ:
        init_engine(os.environ["DATABASE_URL"])

    async with session_factory()() as s:
        live = await s.get(LiveSet, uuid.UUID(live_set_id))
        if live is None:
            return
        live.status = "published"
        await record(
            s,
            kind="set.published",
            subject_type="LiveSet",
            subject_id=live.id,
            user_id=live.uploaded_by,
        )
        await s.commit()

    publish(ProgressEvent(
        kind="ready", live_set_id=live_set_id, job_id=live_set_id,
        progress_pct=100, message="published",
    ))


def mark_ready_sync(live_set_id: str) -> None:
    asyncio.run(mark_ready(live_set_id))
