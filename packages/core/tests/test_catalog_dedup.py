import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import Artist
from setvault_core.services.catalog_dedup import find_duplicate_clusters, normalized_name
from sqlalchemy import delete


@pytest.fixture(autouse=True)
def _engine():
    init_engine(os.environ["TEST_DATABASE_URL"])


@pytest.fixture(autouse=True)
async def _cleanup_artists():
    """Delete Artist rows before and after each test so committed rows don't accumulate."""
    async with session_factory()() as s:
        await s.execute(delete(Artist))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(Artist))
        await s.commit()


def test_normalized_name_folds_case_accents_punct_space():
    assert normalized_name("DJ  X") == normalized_name("dj x")
    assert normalized_name("Café del Mar!") == normalized_name("cafe del mar")
    assert normalized_name("DJ-X") == normalized_name("DJ X")


async def test_find_duplicate_clusters_groups_collisions(session):
    s = session
    a1 = Artist(name="DJ X", slug=f"a-{uuid.uuid4().hex[:6]}")
    a2 = Artist(name="dj  x.", slug=f"b-{uuid.uuid4().hex[:6]}")
    a3 = Artist(name="Someone Else", slug=f"c-{uuid.uuid4().hex[:6]}")
    s.add_all([a1, a2, a3])
    await s.commit()

    clusters = await find_duplicate_clusters(s, kind="artist")
    keys = [sorted(e.name for e in c) for c in clusters]
    assert ["DJ X", "dj  x."] in keys
    # singletons are not returned
    assert all(len(c) >= 2 for c in clusters)
