from __future__ import annotations

import os

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from sqlalchemy import delete

SETUP_EMAIL = "first-admin@example.test"
STRONG = "correct-horse-battery"  # >= 12 chars


def _db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    )


@pytest.fixture
async def fresh_db():
    """Simulate a brand-new install: zero users. LiveSet.uploaded_by is
    ON DELETE RESTRICT, so clear LiveSets before users. Cleans before and
    after so the wizard's count-based gate sees a true fresh DB."""
    init_engine(_db_url())
    async with session_factory()() as s:
        await s.execute(delete(LiveSet))
        await s.execute(delete(User))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(LiveSet))
        await s.execute(delete(User))
        await s.commit()


async def test_status_true_when_no_users(client, fresh_db):
    res = await client.get("/api/setup/status")
    assert res.status_code == 200
    assert res.json()["needs_setup"] is True


async def test_post_creates_admin_and_autologs_in(client, fresh_db):
    res = await client.post(
        "/api/setup", json={"email": SETUP_EMAIL, "password": STRONG}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == SETUP_EMAIL
    assert body["role"] == "admin"
    assert res.cookies.get("session")  # non-empty session cookie = logged in
    assert "csrf_token" in res.cookies


async def test_status_false_after_admin_created(client, fresh_db):
    await client.post("/api/setup", json={"email": SETUP_EMAIL, "password": STRONG})
    res = await client.get("/api/setup/status")
    assert res.json()["needs_setup"] is False


async def test_post_locked_when_user_exists(client, fresh_db):
    await client.post("/api/setup", json={"email": SETUP_EMAIL, "password": STRONG})
    res = await client.post(
        "/api/setup", json={"email": "second@example.test", "password": STRONG}
    )
    assert res.status_code == 409


async def test_post_short_password_rejected(client, fresh_db):
    res = await client.post(
        "/api/setup", json={"email": SETUP_EMAIL, "password": "short"}
    )
    assert res.status_code == 422


async def test_concurrent_submits_create_exactly_one_admin(client, fresh_db, monkeypatch):
    import asyncio

    # Decouple from the auth rate limit: this test asserts the advisory-lock
    # race, not rate limiting. Without this, firing N requests at the default
    # ceiling (5) makes the test silently fragile to that constant.
    monkeypatch.setattr("setvault_web.rate_limit._AUTH_LIMIT", 1000)

    payloads = [
        {"email": f"race{i}@example.test", "password": STRONG} for i in range(8)
    ]
    results = await asyncio.gather(
        *[client.post("/api/setup", json=p) for p in payloads]
    )
    statuses = sorted(r.status_code for r in results)
    assert statuses.count(200) == 1
    assert statuses.count(409) == 7

    from sqlalchemy import func, select

    async with session_factory()() as s:
        count = (await s.execute(select(func.count()).select_from(User))).scalar_one()
    assert count == 1
