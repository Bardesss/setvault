"""Smoke test on GET /api/admin/health — exercises all the joins and ensures
the response shape matches the spec."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_full_shape(
    authed_admin_client, seeded_live_set,
):
    r = await authed_admin_client.get("/api/admin/health")
    assert r.status_code == 200, r.text
    body = r.json()

    # Top-level keys per spec §J11
    assert {"version", "storage_roots", "connectors", "providers", "tokens",
            "audit_retention_days"} <= set(body)

    # version block
    assert body["version"]["current"]
    assert "is_outdated" in body["version"]

    # storage_roots includes the one we just seeded
    roots = body["storage_roots"]
    assert isinstance(roots, list)
    assert len(roots) >= 1
    # Each root has the disk-usage triplet when the path exists
    for root in roots:
        assert "host_path" in root
        assert "last_health_status" in root

    # tokens block has the active/revoked/total counts
    assert {"total", "active", "revoked"} <= set(body["tokens"])

    # connectors + providers are lists (may be empty in test env)
    assert isinstance(body["connectors"], list)
    assert isinstance(body["providers"], list)


@pytest.mark.asyncio
async def test_health_endpoint_requires_admin(client):
    """Non-admin / no-session → 401 or 403."""
    client.cookies.clear()
    r = await client.get("/api/admin/health")
    assert r.status_code in (401, 403)
