async def test_creating_invite_writes_audit_event(authed_admin_client):
    response = await authed_admin_client.post(
        "/api/invites",
        json={"email": "audit@x.test", "role": "user"},
    )
    assert response.status_code == 201
    audit = await authed_admin_client.get("/api/admin/audit?action=invite.created")
    assert audit.status_code == 200
    entries = audit.json()["items"]
    assert any(
        e["action"] == "invite.created"
        and "audit@x.test" in (e["after"] or {}).get("email", "")
        for e in entries
    )
