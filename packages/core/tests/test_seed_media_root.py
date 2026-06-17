import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.jobs.seed_media_root import ensure_default_media_root
from setvault_core.models.catalog import MediaRoot
from sqlalchemy import select


@pytest.fixture(autouse=True)
def _engine():
    init_engine(os.environ["TEST_DATABASE_URL"])


async def test_seeds_default_root_when_none_exist(tmp_path):
    async with session_factory()() as s:
        created = await ensure_default_media_root(s, str(tmp_path), name="Library")
        await s.commit()
        assert created is not None

    async with session_factory()() as s:
        rows = (await s.execute(select(MediaRoot))).scalars().all()
        assert len(rows) == 1
        root = rows[0]
        assert root.name == "Library"
        assert root.host_path == str(tmp_path)
        assert root.enabled is True
        assert root.default_for_ingest is True


async def test_creates_the_directory_when_missing(tmp_path):
    target = tmp_path / "media" / "library"
    assert not target.exists()

    async with session_factory()() as s:
        created = await ensure_default_media_root(s, str(target), name="Library")
        await s.commit()
        assert created is not None

    assert target.is_dir()


async def test_noop_when_a_root_already_exists(tmp_path):
    async with session_factory()() as s:
        existing = MediaRoot(
            name=f"nas-{uuid.uuid4().hex[:6]}", host_path="/mnt/nas",
            enabled=True, default_for_ingest=True,
        )
        s.add(existing)
        await s.commit()
        existing_id = existing.id

    async with session_factory()() as s:
        created = await ensure_default_media_root(s, str(tmp_path), name="Library")
        await s.commit()
        assert created is None

    async with session_factory()() as s:
        rows = (await s.execute(select(MediaRoot))).scalars().all()
        assert len(rows) == 1
        assert rows[0].id == existing_id
