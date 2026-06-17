from __future__ import annotations

import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.services.passwords import hash_password
from setvault_core.services.sessions import SESSION_COOKIE
from setvault_core.services.system_config import get_config


async def _set_flag(value: bool) -> None:
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        cfg = await get_config(s)
        cfg.single_user_auto_login = value
        await s.commit()


@pytest.fixture(autouse=True)
async def _reset_flag():
    """The SystemConfig singleton isn't wiped between tests, so always clear the
    auto-login flag afterwards — otherwise it would leak into other suites and
    silently auto-authenticate their anonymous clients."""
    yield
    await _set_flag(False)


@pytest.mark.asyncio
async def test_settings_exposes_flag_default_false(authed_admin_client):
    r = await authed_admin_client.get("/api/admin/settings")
    assert r.status_code == 200
    assert r.json()["single_user_auto_login"] is False


@pytest.mark.asyncio
async def test_enable_allowed_with_single_user(authed_admin_client, seeded_admin):
    r = await authed_admin_client.put(
        "/api/admin/settings", json={"single_user_auto_login": True}
    )
    assert r.status_code == 200
    assert r.json()["single_user_auto_login"] is True


@pytest.mark.asyncio
async def test_enable_rejected_with_multiple_users(authed_admin_client, seeded_admin):
    init_engine(os.environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        s.add(User(
            email=f"x-{uuid.uuid4().hex[:6]}@x.test",
            username=f"x{uuid.uuid4().hex[:6]}",
            display_name="x", password_hash=hash_password("aaaaaaaa"),
        ))
        await s.commit()
    r = await authed_admin_client.put(
        "/api/admin/settings", json={"single_user_auto_login": True}
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_me_auto_logs_in_the_sole_user_when_enabled(client, seeded_admin):
    await _set_flag(True)
    r = await client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "admin@example.test"
    # a session cookie is minted so subsequent requests are authenticated
    assert SESSION_COOKIE in r.cookies


@pytest.mark.asyncio
async def test_me_401_when_flag_disabled(client, seeded_admin):
    await _set_flag(False)
    r = await client.get("/api/auth/me")
    assert r.status_code == 401
