"""Task 13 — admin settings API surfaces the monitor toggle + poll interval.

SystemConfig is a singleton shared across the test DB and there is no autouse
reset, so this test restores ``monitors_allow_all_users`` back to False in a
``finally`` to avoid leaking True into the Task 11 monitor-gate test
(``test_non_admin_blocked_when_setting_off``)."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_settings_roundtrip_monitor_fields(authed_admin_client):
    # GET current settings — the two new fields are present.
    r = await authed_admin_client.get("/api/admin/settings")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "monitors_allow_all_users" in body
    assert "monitor_interval_seconds" in body

    try:
        # PUT updates them (partial update model — only send what we change).
        r = await authed_admin_client.put(
            "/api/admin/settings",
            json={
                "monitors_allow_all_users": True,
                "monitor_interval_seconds": 1800,
            },
        )
        assert r.status_code in (200, 204), r.text

        r = await authed_admin_client.get("/api/admin/settings")
        body = r.json()
        assert body["monitors_allow_all_users"] is True
        assert body["monitor_interval_seconds"] == 1800
    finally:
        # Restore defaults so the monitor-gate test elsewhere keeps passing.
        await authed_admin_client.put(
            "/api/admin/settings",
            json={
                "monitors_allow_all_users": False,
                "monitor_interval_seconds": 3600,
            },
        )


@pytest.mark.asyncio
async def test_settings_requires_admin(client):
    client.cookies.clear()
    r = await client.get("/api/admin/settings")
    assert r.status_code in (401, 403)
    r = await client.put("/api/admin/settings", json={"monitor_interval_seconds": 1800})
    assert r.status_code in (401, 403)
