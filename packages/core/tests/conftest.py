import os
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


def _get_test_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL")


@pytest.fixture(scope="session", autouse=True)
def _check_db_url():
    """Skip entire session if TEST_DATABASE_URL is not set."""
    url = _get_test_url()
    if not url:
        pytest.skip("TEST_DATABASE_URL not set", allow_module_level=True)


@pytest.fixture
async def session():
    """Provide a fresh AsyncSession per test using NullPool to avoid event-loop conflicts."""
    url = _get_test_url()
    engine = create_async_engine(url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s
        await s.rollback()
    await engine.dispose()


@pytest.fixture
def uid() -> uuid.UUID:
    return uuid.uuid4()
