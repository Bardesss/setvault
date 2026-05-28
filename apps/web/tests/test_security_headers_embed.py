from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_default_route_has_frame_deny(client):
    """Non-embed routes keep X-Frame-Options: DENY and the strict CSP."""
    r = await client.get("/api/health")
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "frame-ancestors 'none'" in r.headers.get("Content-Security-Policy", "")


@pytest.mark.asyncio
async def test_embed_api_drops_xfo_and_allows_frame_ancestors(client, seeded_live_set):
    """/api/sets/.../embed must drop X-Frame-Options and use frame-ancestors *."""
    r = await client.get(f"/api/sets/{seeded_live_set['slug']}/embed")
    # 404 is fine - we're testing headers, not the body
    assert "X-Frame-Options" not in r.headers
    assert "frame-ancestors *" in r.headers.get("Content-Security-Policy", "")
