from __future__ import annotations

import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.models.url_rip import RipJob
from setvault_core.services.passwords import hash_password


async def _seed_job(submitted_by: uuid.UUID, status: str = "ready") -> uuid.UUID:
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        job = RipJob(
            source_url=f"https://youtu.be/{uuid.uuid4().hex[:8]}",
            source_platform="youtube",
            status=status,
            submitted_by=submitted_by,
        )
        s.add(job)
        await s.commit()
        return job.id


@pytest.mark.asyncio
async def test_delete_own_rip_job(authed_admin_client, seeded_admin):
    job_id = await _seed_job(seeded_admin.id, status="failed")
    r = await authed_admin_client.delete(f"/api/me/rip-jobs/{job_id}")
    assert r.status_code == 204
    lst = await authed_admin_client.get("/api/me/rip-jobs")
    assert all(i["id"] != str(job_id) for i in lst.json()["items"])


@pytest.mark.asyncio
async def test_cannot_delete_another_users_rip_job(authed_admin_client):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        other = User(
            email=f"o-{uuid.uuid4().hex[:6]}@x.test",
            username=f"o{uuid.uuid4().hex[:6]}",
            display_name="o", password_hash=hash_password("aaaaaaaa"),
        )
        s.add(other)
        await s.commit()
        other_id = other.id
    job_id = await _seed_job(other_id, status="failed")
    r = await authed_admin_client.delete(f"/api/me/rip-jobs/{job_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_clear_finished_keeps_active(authed_admin_client, seeded_admin):
    ready = await _seed_job(seeded_admin.id, status="ready")
    failed = await _seed_job(seeded_admin.id, status="failed")
    active = await _seed_job(seeded_admin.id, status="downloading")
    r = await authed_admin_client.delete("/api/me/rip-jobs")
    assert r.status_code == 204
    lst = await authed_admin_client.get("/api/me/rip-jobs")
    ids = {i["id"] for i in lst.json()["items"]}
    assert str(active) in ids
    assert str(ready) not in ids
    assert str(failed) not in ids
