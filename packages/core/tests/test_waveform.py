import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.jobs.waveform import generate_waveform
from setvault_core.models.catalog import LiveSet, MediaRoot
from setvault_core.models.identity import User


@pytest.fixture(autouse=True)
def _engine():
    init_engine(os.environ["TEST_DATABASE_URL"])


async def test_waveform_writes_peaks_json(tmp_path: Path):
    if not shutil.which("audiowaveform") or not shutil.which("ffmpeg"):
        pytest.skip("audiowaveform + ffmpeg required")
    src = tmp_path / "audio.flac"
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i",
           "sine=frequency=1000:duration=3", str(src)]
    subprocess.run(cmd, check=True, capture_output=True)  # noqa: ASYNC221, S603
    async with session_factory()() as s:
        u = User(email=f"u{uuid.uuid4().hex[:6]}@x.test", username=f"u{uuid.uuid4().hex[:6]}",
                 display_name="u", password_hash="x", role="admin")
        r = MediaRoot(name=f"r{uuid.uuid4().hex[:6]}", host_path=str(tmp_path),
                      enabled=True, default_for_ingest=True)
        s.add_all([u, r])
        await s.flush()
        live = LiveSet(slug=f"s-{uuid.uuid4().hex[:6]}", title="t", media_root_id=r.id,
                       audio_path="audio.flac", uploaded_by=u.id, source_type="upload",
                       status="processing", duration_seconds=3)
        s.add(live)
        await s.commit()
        sid = live.id

    await generate_waveform(str(sid))

    async with session_factory()() as s:
        row = await s.get(LiveSet, sid)
        assert row.waveform_path == f"waveform/{sid}.json"
        peaks = json.loads((tmp_path / row.waveform_path).read_text())
        assert "data" in peaks and len(peaks["data"]) > 0
