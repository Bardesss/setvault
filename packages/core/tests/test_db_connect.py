import os

import pytest
from sqlalchemy import text

from setvault_core.db import session_factory, init_engine


@pytest.fixture(autouse=True)
def _engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    init_engine(url)


async def test_can_select_one():
    async with session_factory()() as session:
        result = await session.execute(text("select 1"))
        assert result.scalar_one() == 1
