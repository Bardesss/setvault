import pytest
from httpx import ASGITransport, AsyncClient

from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.services.passwords import hash_password


@pytest.fixture
async def client():
    from setvault_web.main import create_app
    app = create_app()
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
