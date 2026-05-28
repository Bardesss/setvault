"""API tests for POST /api/sets/bulk-action.

Exercises gating + payload validation. The actual worker execution lives in
test_bulk_action.py and (at integration scope) the e2e Playwright suite —
we don't have a worker running during pytest, so the endpoint just verifies
the enqueue succeeds.
"""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_bulk_action_requires_admin(client, seeded_live_set):
    """Non-admin / no-session POST returns 401 or 403."""
    client.cookies.clear()
    r = await client.post("/api/sets/bulk-action", json={
        "action": "soft_delete",
        "set_ids": [seeded_live_set["id"]],
        "params": {},
    })
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_bulk_action_unknown_action_returns_400(authed_admin_client, seeded_live_set):
    r = await authed_admin_client.post("/api/sets/bulk-action", json={
        "action": "drop_database",
        "set_ids": [seeded_live_set["id"]],
        "params": {},
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_bulk_action_empty_set_ids_returns_400(authed_admin_client):
    r = await authed_admin_client.post("/api/sets/bulk-action", json={
        "action": "soft_delete",
        "set_ids": [],
        "params": {},
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_bulk_action_soft_delete_enqueues_202(authed_admin_client, seeded_live_set):
    r = await authed_admin_client.post("/api/sets/bulk-action", json={
        "action": "soft_delete",
        "set_ids": [seeded_live_set["id"]],
        "params": {},
    })
    assert r.status_code == 202, r.text
    body = r.json()
    assert body["status"] == "queued"
    assert body["action"] == "soft_delete"
    assert body["count"] == 1
    assert "job_id" in body
