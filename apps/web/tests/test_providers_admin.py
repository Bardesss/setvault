import pytest


@pytest.mark.asyncio
async def test_create_provider_returns_redacted_config(authed_admin_client):
    r = await authed_admin_client.put("/api/admin/providers/musicbrainz", json={
        "name": "MusicBrainz",
        "enabled": True,
        "priority": 10,
        "config": {"user_agent": "MyApp/1.0 (me@example.com)"},
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider_kind"] == "musicbrainz"
    assert body["enabled"] is True
    assert "user_agent" not in body


@pytest.mark.asyncio
async def test_list_providers_filters_by_kind(authed_admin_client):
    await authed_admin_client.put("/api/admin/providers/musicbrainz",
                                  json={"name": "MB", "config": {"user_agent": "x"}})
    await authed_admin_client.put("/api/admin/providers/discogs",
                                  json={"name": "D", "config": {"token": "t"}})
    r = await authed_admin_client.get("/api/admin/providers")
    assert r.status_code == 200
    items = r.json()["items"]
    kinds = {p["provider_kind"] for p in items}
    assert {"musicbrainz", "discogs"} <= kinds


@pytest.mark.asyncio
async def test_non_admin_forbidden(client, seeded_admin):
    r = await client.get("/api/admin/providers")
    assert r.status_code in (401, 403)
