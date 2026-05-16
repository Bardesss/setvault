async def test_admin_can_create_and_list_media_root(authed_admin_client, tmp_path):
    response = await authed_admin_client.post("/api/media-roots", json={
        "name": "primary", "host_path": str(tmp_path),
        "default_for_ingest": True, "naming_template": None, "max_bytes": None,
    })
    assert response.status_code == 201
    listed = await authed_admin_client.get("/api/media-roots")
    names = [r["name"] for r in listed.json()["items"]]
    assert "primary" in names


async def test_creating_root_at_nonexistent_path_warns_but_succeeds(authed_admin_client):
    response = await authed_admin_client.post("/api/media-roots", json={
        "name": "missing", "host_path": "/nonexistent/path/setvault",
        "default_for_ingest": False, "naming_template": None, "max_bytes": None,
    })
    assert response.status_code == 201
    body = response.json()
    assert body["last_health_status"] in ("unreachable", "unknown")
