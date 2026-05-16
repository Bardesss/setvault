from __future__ import annotations

import asyncio
import os
import subprocess
import uuid
from pathlib import Path

from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import LiveSet, MediaRoot
from setvault_core.progress import ProgressEvent, publish


async def generate_waveform(live_set_id: str) -> None:
    if "DATABASE_URL" in os.environ:
        init_engine(os.environ["DATABASE_URL"])

    async with session_factory()() as s:
        live = await s.get(LiveSet, uuid.UUID(live_set_id))
        if live is None:
            raise RuntimeError(f"LiveSet {live_set_id} missing")
        root = await s.get(MediaRoot, live.media_root_id)
        if root is None:
            raise RuntimeError("MediaRoot vanished")
        src = Path(root.host_path) / live.audio_path
        rel = f"waveform/{live.id}.json"
        dest = Path(root.host_path) / rel
        tmp = dest.with_suffix(".json.tmp")
        dest.parent.mkdir(parents=True, exist_ok=True)

        publish(ProgressEvent(
            kind="waveform", live_set_id=live_set_id, job_id=live_set_id,
            progress_pct=85, message="computing peaks",
        ))
        pixels_per_second = 20
        cmd = [
            "audiowaveform", "-i", str(src), "-o", str(tmp),
            "--output-format", "json",
            "--pixels-per-second", str(pixels_per_second),
            "--bits", "8",
        ]
        await asyncio.to_thread(
            subprocess.run, cmd,
            check=True, capture_output=True,
        )
        tmp.replace(dest)

        live.waveform_path = rel
        await s.commit()
        publish(ProgressEvent(
            kind="waveform", live_set_id=live_set_id, job_id=live_set_id,
            progress_pct=95, message="peaks written",
        ))


def generate_waveform_sync(live_set_id: str) -> None:
    asyncio.run(generate_waveform(live_set_id))
