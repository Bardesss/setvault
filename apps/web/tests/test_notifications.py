async def test_mention_creates_in_app_notification(authed_admin_client, seeded_live_set, client):
    # Create a second user "alice" via the seeded-admin invite flow
    invite = await authed_admin_client.post(
        "/api/invites", json={"email": "alice@x.test", "role": "user"}
    )
    assert invite.status_code in (200, 201)
    token = invite.json()["invite_link"].rsplit("/", 1)[-1]
    redeemed = await client.post(
        f"/api/invites/{token}/redeem",
        json={
            "username": "alice",
            "password": "alicealice123",
            "display_name": "Alice",
        },
    )
    assert redeemed.status_code == 200

    # The redeem call overwrites session/csrf cookies on the shared client; log
    # the admin back in so we can post a comment as them.
    admin_login = await client.post(
        "/api/auth/login",
        json={"email": "admin@example.test", "password": "hunter2hunter2"},
    )
    assert admin_login.status_code == 200
    client.cookies = admin_login.cookies
    client.headers["X-CSRF-Token"] = admin_login.cookies["csrf_token"]

    slug = seeded_live_set["slug"]
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/comments",
        json={"body": "Hey @alice, check this drop!"},
    )
    assert r.status_code == 201

    # Now log in as alice and check her notification feed
    alice_login = await client.post(
        "/api/auth/login",
        json={"email": "alice@x.test", "password": "alicealice123"},
    )
    client.cookies = alice_login.cookies
    client.headers["X-CSRF-Token"] = alice_login.cookies["csrf_token"]
    feed = await client.get("/api/me/notifications")
    assert feed.status_code == 200, feed.text
    body = feed.json()
    assert body["unread_count"] >= 1
    assert any(n["kind"] == "mention" for n in body["items"])
