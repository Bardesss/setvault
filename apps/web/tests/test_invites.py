

async def test_admin_can_create_invite_and_link_is_returned(authed_admin_client):
    response = await authed_admin_client.post(
        "/api/invites",
        json={"email": "new@example.test", "role": "user"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.test"
    assert body["invite_link"].startswith("https://test/invite/")
    assert body["smtp_sent"] is False


async def test_redeem_invite_creates_user_and_logs_in(client, authed_admin_client):
    create = await authed_admin_client.post("/api/invites",
                                            json={"email": "new@example.test", "role": "user"})
    token = create.json()["invite_link"].rsplit("/", 1)[-1]
    redeem = await client.post(f"/api/invites/{token}/redeem", json={
        "username": "new", "display_name": "New User", "password": "correct horse",
    })
    assert redeem.status_code == 200
    assert redeem.json()["user"]["email"] == "new@example.test"
    assert "session" in redeem.cookies


async def test_redeem_invite_twice_fails(client, authed_admin_client):
    create = await authed_admin_client.post("/api/invites",
                                            json={"email": "x@x.test", "role": "user"})
    token = create.json()["invite_link"].rsplit("/", 1)[-1]
    first = await client.post(f"/api/invites/{token}/redeem", json={
        "username": "x", "display_name": "X", "password": "correct horse",
    })
    assert first.status_code == 200
    second = await client.post(f"/api/invites/{token}/redeem", json={
        "username": "y", "display_name": "Y", "password": "correct horse",
    })
    assert second.status_code in (400, 410)
