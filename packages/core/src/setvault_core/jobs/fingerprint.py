from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import uuid
from pathlib import Path

from sqlalchemy import select

from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import LiveSet, MediaRoot, SetFingerprint
from setvault_core.progress import ProgressEvent, publish


async def fingerprint_audio(live_set_id: str) -> None:
    if "DATABASE_URL" in os.environ:
        init_engine(os.environ["DATABASE_URL"])

    async with session_factory()() as s:
        live = await s.get(LiveSet, uuid.UUID(live_set_id))
        if live is None:
            raise RuntimeError(f"LiveSet {live_set_id} missing")
        root = await s.get(MediaRoot, live.media_root_id)
        if root is None:
            raise RuntimeError("MediaRoot vanished")
        path = Path(root.host_path) / live.audio_path

        publish(ProgressEvent(
            kind="fingerprint", live_set_id=live_set_id, job_id=live_set_id,
            progress_pct=20, message="fingerprinting",
        ))

        out = await asyncio.to_thread(
            subprocess.run, ["fpcalc", "-json", str(path)],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(out.stdout)
        fp = data["fingerprint"]
        duration = float(data.get("duration", live.duration_seconds or 0))
        digest = hashlib.sha256(fp.encode("ascii")).hexdigest()

        existing = (await s.execute(
            select(SetFingerprint).where(SetFingerprint.fingerprint_hash == digest),
        )).scalar_one_or_none()
        if (
            existing
            and existing.live_set_id != live.id
            and abs(existing.duration_seconds - duration) < 2
        ):
            live.duplicate_of = existing.live_set_id
        s.add(SetFingerprint(
            live_set_id=live.id, fingerprint_hash=digest, duration_seconds=duration,
        ))
        await s.commit()

        publish(ProgressEvent(
            kind="fingerprint", live_set_id=live_set_id, job_id=live_set_id,
            progress_pct=30,
            message=(
                "duplicate of existing set" if live.duplicate_of
                else "unique fingerprint"
            ),
        ))


def fingerprint_audio_sync(live_set_id: str) -> None:
    asyncio.run(fingerprint_audio(live_set_id))
