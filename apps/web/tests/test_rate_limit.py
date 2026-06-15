import types

import pytest


@pytest.fixture(autouse=True)
def _db():
    import os
    os.environ.setdefault(
        "TEST_DATABASE_URL", "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault"
    )


async def test_login_rate_limit_kicks_in_after_5(client, monkeypatch):
    # Pin the rate limiter's clock so all six attempts share one 60s bucket.
    # With a real clock the requests can straddle a bucket boundary mid-test
    # (more likely under the test suite's NullPool, which makes each request
    # slower), resetting the counter and flaking the 429 assertion. Patches only
    # the `time` reference inside the rate_limit module, not the global clock.
    monkeypatch.setattr(
        "setvault_web.rate_limit.time",
        types.SimpleNamespace(time=lambda: 1_000_000.0),
    )
    for _ in range(5):
        r = await client.post("/api/auth/login",
                              json={"email": "nobody@x.test", "password": "x"})
        assert r.status_code == 401
    r = await client.post("/api/auth/login",
                          json={"email": "nobody@x.test", "password": "x"})
    assert r.status_code == 429
