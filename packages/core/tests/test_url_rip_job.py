from __future__ import annotations

import subprocess
import uuid
from datetime import UTC, datetime

import pytest
from setvault_core.jobs.url_rip_job import _error_text, _run_rip_job, _set_status
from setvault_core.models.identity import User
from setvault_core.models.url_rip import RipJob
from setvault_core.services.passwords import hash_password


async def _make_user(session):
    user = User(
        email=f"u-{uuid.uuid4().hex[:6]}@x.test",
        username=f"u{uuid.uuid4().hex[:6]}",
        display_name="u",
        password_hash=hash_password("aaaaaaaa"),
    )
    session.add(user)
    await session.flush()
    return user


def test_error_text_surfaces_subprocess_stderr():
    """A failing ffmpeg/audiowaveform step must surface its stderr, not just
    'returned non-zero exit status 1' — that's what makes a rip debuggable."""
    exc = subprocess.CalledProcessError(
        1, ["audiowaveform", "--input-format", "wav", "-i", "-"],
        stderr=b"Error: Unknown input format\n",
    )
    text = _error_text(exc)
    assert "audiowaveform" in text
    assert "Unknown input format" in text


@pytest.mark.asyncio
async def test_set_status_updates_row(session):
    """_set_status(job, 'downloading', progress_pct=15) mutates the row in place."""
    user = await _make_user(session)
    await session.commit()

    job = RipJob(
        submitted_by=user.id, source_url="https://x", status="queued", progress_pct=0,
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    session.add(job)
    await session.flush()

    await _set_status(session, job, "downloading", progress_pct=15, message="fetching audio")
    assert job.status == "downloading"
    assert job.progress_pct == 15
    assert job.message == "fetching audio"
    assert job.started_at is not None


@pytest.mark.asyncio
async def test_run_rip_job_failure_captures_error(session, monkeypatch):
    """If the download step raises, the job ends in status='failed' with error_text set."""
    from setvault_core.models.catalog import MediaRoot

    user = await _make_user(session)
    root = MediaRoot(
        name=f"r-{uuid.uuid4().hex[:6]}", host_path="/srv/test-media",
        default_for_ingest=True,
    )
    session.add(root)
    await session.commit()

    job = RipJob(
        submitted_by=user.id, source_url="https://x", status="queued", progress_pct=0,
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    session.add(job)
    await session.commit()
    job_id = job.id

    async def _boom(*a, **kw):
        raise RuntimeError("yt-dlp boom")

    monkeypatch.setattr("setvault_core.jobs.url_rip_job._download", _boom)

    await _run_rip_job(session, job_id)
    await session.refresh(job)
    assert job.status == "failed"
    # This is a self-hosted single-user app: surface the real exception (type +
    # message) so failures are debuggable from the UI. Full traceback still goes
    # to the worker log.
    assert "yt-dlp boom" in (job.error_text or "")
    assert "RuntimeError" in (job.error_text or "")
