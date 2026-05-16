import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.jobs.media_root_health import run_health_checks
from setvault_core.models.catalog import MediaRoot


@pytest.fixture(autouse=True)
def _engine():
    init_engine(os.environ["TEST_DATABASE_URL"])


async def test_health_check_updates_status(tmp_path):
    async with session_factory()() as s:
        r = MediaRoot(name=f"hc-{uuid.uuid4().hex[:6]}", host_path=str(tmp_path),
                      enabled=True, default_for_ingest=False)
        s.add(r)
        await s.commit()
        rid = r.id

    await run_health_checks()

    async with session_factory()() as s:
        row = await s.get(MediaRoot, rid)
        assert row.last_health_status == "ok"
        assert row.last_health_check_at is not None
