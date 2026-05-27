import pytest


@pytest.mark.asyncio
async def test_create_and_list_comment(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    r = await authed_admin_client.post(f"/api/sets/{slug}/comments", json={
        "body": "hello **world**",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert "<strong>world</strong>" in body["body_html"]
    listing = await authed_admin_client.get(f"/api/sets/{slug}/comments")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


@pytest.mark.asyncio
async def test_reply_one_level(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    top = (await authed_admin_client.post(f"/api/sets/{slug}/comments",
                                           json={"body": "top"})).json()
    r = await authed_admin_client.post(f"/api/sets/{slug}/comments", json={
        "body": "reply", "parent_id": top["id"],
    })
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_reply_to_reply_rejected(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    top = (await authed_admin_client.post(f"/api/sets/{slug}/comments",
                                           json={"body": "top"})).json()
    reply = (await authed_admin_client.post(f"/api/sets/{slug}/comments",
                                             json={"body": "reply", "parent_id": top["id"]})).json()
    r = await authed_admin_client.post(f"/api/sets/{slug}/comments", json={
        "body": "second-level reply", "parent_id": reply["id"],
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_edit_within_window(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    c = (await authed_admin_client.post(f"/api/sets/{slug}/comments",
                                          json={"body": "original"})).json()
    r = await authed_admin_client.patch(f"/api/comments/{c['id']}",
                                          json={"body": "edited"})
    assert r.status_code == 200
    assert "edited" in r.json()["body_md"]


@pytest.mark.asyncio
async def test_soft_delete(authed_admin_client, seeded_live_set):
    slug = seeded_live_set["slug"]
    c = (await authed_admin_client.post(f"/api/sets/{slug}/comments",
                                          json={"body": "delete me"})).json()
    r = await authed_admin_client.delete(f"/api/comments/{c['id']}")
    assert r.status_code == 204
    listing = (await authed_admin_client.get(f"/api/sets/{slug}/comments")).json()
    assert listing["items"][0]["deleted_at"] is not None
