from __future__ import annotations


async def test_tusd_pre_create_hook_accepts_authenticated(authed_admin_client, tmp_path):
    create = await authed_admin_client.post("/api/media-roots", json={
        "name": "primary", "host_path": str(tmp_path), "default_for_ingest": True,
        "naming_template": None, "max_bytes": None,
    })
    assert create.status_code == 201
    cookie = authed_admin_client.cookies.get("session")
    response = await authed_admin_client.post(
        "/api/uploads/tusd-hooks",
        json={
            "Type": "pre-create",
            "Event": {
                "Upload": {
                    "MetaData": {"filename": "set.flac", "filetype": "audio/flac"},
                },
                "HTTPRequest": {"Header": {"Cookie": [f"session={cookie}"]}},
            },
        },
    )
    assert response.status_code == 200


async def test_post_finish_hook_creates_live_set_and_enqueues_pipeline(
    authed_admin_client, tmp_path, monkeypatch,
):
    enqueued: list[tuple[str, dict]] = []

    class _FakeJob:
        id = "test-job-id"

    class _FakeQueue:
        def enqueue(self, func, **kwargs):
            enqueued.append((func, kwargs))
            return _FakeJob()

    from setvault_web import tusd_hooks

    monkeypatch.setattr(tusd_hooks, "queue", lambda: _FakeQueue())
    monkeypatch.setattr(tusd_hooks, "sniff_mime", lambda p: "audio/flac")

    await authed_admin_client.post("/api/media-roots", json={
        "name": "primary", "host_path": str(tmp_path), "default_for_ingest": True,
        "naming_template": None, "max_bytes": None,
    })
    upload_dir = tmp_path / "tus"
    upload_dir.mkdir()
    src = upload_dir / "abc123"
    src.write_bytes(b"fake-audio-bytes")
    cookie = authed_admin_client.cookies.get("session")
    response = await authed_admin_client.post(
        "/api/uploads/tusd-hooks",
        json={
            "Type": "post-finish",
            "Event": {
                "Upload": {
                    "ID": "abc123",
                    "Size": len(b"fake-audio-bytes"),
                    "Storage": {"Path": str(src), "Type": "filestore"},
                    "MetaData": {"filename": "set.flac", "filetype": "audio/flac"},
                },
                "HTTPRequest": {"Header": {"Cookie": [f"session={cookie}"]}},
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["live_set_id"]
    assert enqueued and enqueued[0][0] == "setvault_core.jobs.pipeline.run_pipeline"
