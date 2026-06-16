import os
import uuid

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.services.passwords import hash_password


@pytest.mark.asyncio
async def test_admin_can_create_and_list_monitor(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/monitors", json={"kind": "query", "query_text": "Bicep"}
    )
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    r = await authed_admin_client.get("/api/monitors")
    assert r.status_code == 200, r.text
    assert any(m["id"] == mid for m in r.json()["items"])


@pytest.mark.asyncio
async def test_delete_monitor(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/monitors", json={"kind": "query", "query_text": "y"}
    )
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    r = await authed_admin_client.delete(f"/api/monitors/{mid}")
    assert r.status_code == 204, r.text


@pytest.mark.asyncio
async def test_non_admin_blocked_when_setting_off(client):
    # Seed a NON-admin user (default monitors_allow_all_users is False).
    init_engine(os.environ["TEST_DATABASE_URL"])
    email = f"u-{uuid.uuid4().hex[:6]}@x.test"
    password = "hunter2hunter2"
    async with session_factory()() as s:
        u = User(
            email=email,
            username=f"u{uuid.uuid4().hex[:6]}",
            display_name="u",
            password_hash=hash_password(password),
            role="user",
        )
        s.add(u)
        await s.commit()

    login = await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert login.status_code == 200, login.text
    client.cookies = login.cookies
    client.headers["X-CSRF-Token"] = login.cookies["csrf_token"]

    r = await client.post("/api/monitors", json={"kind": "query", "query_text": "x"})
    assert r.status_code == 403, r.text
