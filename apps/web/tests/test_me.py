async def test_continue_listening_empty_for_new_user(authed_admin_client):
    response = await authed_admin_client.get("/api/me/continue-listening")
    assert response.status_code == 200
    assert response.json() == []


async def test_continue_listening_returns_in_progress_sets(
    authed_admin_client, seeded_live_set
):
    slug = seeded_live_set["slug"]
    put = await authed_admin_client.put(
        f"/api/sets/{slug}/state",
        json={"position_seconds": 12.5, "completed": False},
    )
    assert put.status_code == 204
    response = await authed_admin_client.get("/api/me/continue-listening")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["slug"] == slug
    assert items[0]["position_seconds"] == 12.5


async def test_continue_listening_excludes_completed(
    authed_admin_client, seeded_live_set
):
    slug = seeded_live_set["slug"]
    await authed_admin_client.put(
        f"/api/sets/{slug}/state",
        json={"position_seconds": 999.0, "completed": True},
    )
    response = await authed_admin_client.get("/api/me/continue-listening")
    assert response.status_code == 200
    assert response.json() == []


async def test_activity_returns_array(authed_admin_client):
    response = await authed_admin_client.get("/api/me/activity")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_me_endpoints_require_auth(client):
    response = await client.get("/api/me/continue-listening")
    assert response.status_code == 401
