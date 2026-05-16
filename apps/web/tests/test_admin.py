async def test_system_info_returns_version(authed_admin_client):
    response = await authed_admin_client.get("/api/admin/system")
    assert response.status_code == 200
    body = response.json()
    assert body["version"]
    # secrets must be filtered
    assert "secret_key" not in body["env"]


async def test_jobs_listing_is_admin_only(client, seeded_admin):
    response = await client.get("/api/admin/jobs")
    assert response.status_code in (401, 403)


async def test_users_listing_includes_admin(authed_admin_client):
    response = await authed_admin_client.get("/api/users")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(u["email"] == "admin@example.test" for u in items)
