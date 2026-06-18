import os
import uuid
from datetime import UTC, datetime

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist


@pytest.fixture
async def tombstoned_artist(seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        survivor = Artist(name="Keep", slug=f"keep-{uuid.uuid4().hex[:6]}")
        s.add(survivor)
        await s.flush()
        dead = Artist(name="Gone", slug=f"gone-{uuid.uuid4().hex[:6]}",
                      merged_into_id=survivor.id, merged_at=datetime.now(UTC))
        s.add(dead)
        await s.commit()
        yield dead.slug


@pytest.mark.asyncio
async def test_get_tombstoned_artist_404(authed_admin_client, tombstoned_artist):
    r = await authed_admin_client.get(f"/api/catalog/artists/{tombstoned_artist}")
    assert r.status_code == 404
