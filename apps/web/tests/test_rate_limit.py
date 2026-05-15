import pytest


@pytest.fixture(autouse=True)
def _db():
    import os
    os.environ.setdefault(
        "TEST_DATABASE_URL", "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault"
    )


async def test_login_rate_limit_kicks_in_after_5(client):
    for _ in range(5):
        r = await client.post("/api/auth/login",
                              json={"email": "nobody@x.test", "password": "x"})
        assert r.status_code == 401
    r = await client.post("/api/auth/login",
                          json={"email": "nobody@x.test", "password": "x"})
    assert r.status_code == 429
