import pytest
from httpx import ASGITransport, AsyncClient

from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.services.passwords import hash_password


@pytest.fixture(autouse=True)
async def _reset_rate_limit():
    import setvault_web.rate_limit as _rl
    from redis.asyncio import Redis

    from setvault_web.config import get_settings

    # Reset the module-level singleton so each test gets a fresh connection
    # (each test runs in its own asyncio event loop; old transports are closed)
    if _rl._redis is not None:
        try:
            await _rl._redis.aclose()
        except Exception:
            pass
        _rl._redis = None

    r = Redis.from_url(get_settings().redis_url, decode_responses=True)
    keys = await r.keys("rl:*")
    if keys:
        await r.delete(*keys)
    await r.aclose()
    yield


@pytest.fixture
async def client():
    import os

    from setvault_core.db import init_engine
    from setvault_web.main import create_app

    app = create_app()
    # Override engine with test DB URL so tests never touch the docker-internal hostname
    test_db_url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    )
    init_engine(test_db_url)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="https://test", follow_redirects=False
    ) as ac:
        yield ac


@pytest.fixture
async def seeded_admin():
    init_engine(__import__("os").environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        user = User(
            email="admin@example.test", username="admin", display_name="Admin",
            password_hash=hash_password("hunter2hunter2"), role="admin",
        )
        s.add(user)
        await s.commit()
        yield user
        await s.delete(user)
        await s.commit()
