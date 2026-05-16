import uuid

from setvault_core.db import session_factory
from setvault_core.models.catalog import LiveSet
from setvault_core.models.identity import User
from sqlalchemy import select


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


async def test_admin_can_delete_unused_media_root(authed_admin_client, tmp_path):
    created = await authed_admin_client.post("/api/media-roots", json={
        "name": "to-delete", "host_path": str(tmp_path),
        "default_for_ingest": False, "naming_template": None, "max_bytes": None,
    })
    rid = created.json()["id"]
    response = await authed_admin_client.delete(f"/api/media-roots/{rid}")
    assert response.status_code == 204
    listed = await authed_admin_client.get("/api/media-roots")
    assert rid not in [r["id"] for r in listed.json()["items"]]


async def test_delete_media_root_conflicts_when_liveset_references_it(
    authed_admin_client, tmp_path
):
    created = await authed_admin_client.post("/api/media-roots", json={
        "name": "with-set", "host_path": str(tmp_path),
        "default_for_ingest": False, "naming_template": None, "max_bytes": None,
    })
    rid = created.json()["id"]

    # Seed a LiveSet that points at this root
    async with session_factory()() as s:
        admin = (await s.execute(
            select(User).where(User.email == "admin@example.test")
        )).scalar_one()
        ls = LiveSet(
            media_root_id=uuid.UUID(rid),
            title="test set",
            slug=f"test-set-{uuid.uuid4().hex[:8]}",
            audio_path="audio.flac",
            uploaded_by=admin.id,
        )
        s.add(ls)
        await s.commit()
        ls_id = ls.id

    try:
        response = await authed_admin_client.delete(f"/api/media-roots/{rid}")
        assert response.status_code == 409
    finally:
        async with session_factory()() as s:
            row = await s.get(LiveSet, ls_id)
            if row is not None:
                await s.delete(row)
                await s.commit()
