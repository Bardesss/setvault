async def test_create_smtp_connector_and_round_trip_secret(authed_admin_client):
    response = await authed_admin_client.post("/api/connectors", json={
        "kind": "smtp", "name": "default",
        "config": {
            "host": "smtp.example.test", "port": 587, "encryption": "starttls",
            "username": "noreply", "password": "shhh-secret",
            "from_email": "noreply@setvault.test", "from_name": "SetVault",
            "reply_to": None,
        },
        "scope_filter": {"kinds": ["*"]},
        "enabled": True,
    })
    assert response.status_code == 201
    cid = response.json()["id"]
    # GET must not echo the plaintext password
    show = await authed_admin_client.get(f"/api/connectors/{cid}")
    assert show.status_code == 200
    body = show.json()
    assert body["config"]["host"] == "smtp.example.test"
    assert "password" not in body["config"]
    assert body["config"]["password_set"] is True


async def test_test_send_uses_dry_run_in_tests(authed_admin_client):
    create = await authed_admin_client.post("/api/connectors", json={
        "kind": "smtp", "name": "default",
        "config": {"host": "smtp.example.test", "port": 25, "encryption": "none",
                   "username": None, "password": None,
                   "from_email": "n@x.test", "from_name": "X", "reply_to": None},
        "scope_filter": {"kinds": ["*"]}, "enabled": True,
    })
    cid = create.json()["id"]
    response = await authed_admin_client.post(f"/api/connectors/{cid}/test-send",
                                              json={"to": "rcpt@example.test", "dry_run": True})
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["dry_run"] is True
