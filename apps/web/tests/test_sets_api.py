async def test_list_sets_returns_only_published(authed_admin_client, seeded_live_set):
    response = await authed_admin_client.get("/api/sets")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "published"


async def test_get_set_by_slug(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    response = await authed_admin_client.get(f"/api/sets/{slug}")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == slug
    assert body["audio_stream_url"].endswith(f"/api/sets/{slug}/stream")


async def test_edit_set_replaces_artists_and_tags(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    artist = await authed_admin_client.post("/api/catalog/artists", json={"name": "Jeff Mills"})
    response = await authed_admin_client.patch(f"/api/sets/{slug}", json={
        "title": "Renamed",
        "artist_ids": [artist.json()["id"]],
        "tag_names": ["techno", "vinyl"],
    })
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Renamed"
    assert [a["name"] for a in body["artists"]] == ["Jeff Mills"]
    assert sorted(body["tags"]) == ["techno", "vinyl"]


async def test_soft_delete_hides_from_list(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    await authed_admin_client.delete(f"/api/sets/{slug}")
    listed = await authed_admin_client.get("/api/sets")
    assert listed.json()["items"] == []
