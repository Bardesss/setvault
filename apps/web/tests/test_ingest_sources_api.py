from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.url_rip import RipJob
from setvault_ingest_sources.base import Candidate


@pytest.fixture
async def seeded_youtube_ripjob():
    """Insert a non-failed youtube RipJob with external id `known1`, committed so
    the search endpoint's already-in-library query sees it. The autouse
    `_cleanup_rip_jobs` fixture wipes rip_jobs before/after each test."""
    init_engine(__import__("os").environ["TEST_DATABASE_URL"])
    async with session_factory()() as s:
        job = RipJob(
            source_url="https://youtu.be/known1",
            source_platform="youtube",
            source_external_id="known1",
            status="completed",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        s.add(job)
        await s.commit()
    yield


@pytest.mark.asyncio
async def test_search_requires_auth(client):
    r = await client.post("/api/ingest-sources/search", json={"q": "x"})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_search_returns_candidates_with_library_flag(
    authed_admin_client, seeded_youtube_ripjob
):
    cands = [
        Candidate("youtube", "known1", "Already", "U", 60, None, "https://youtu.be/known1"),
        Candidate("youtube", "new2", "Fresh", "U", 60, None, "https://youtu.be/new2"),
    ]
    with patch("setvault_web.api.ingest_sources.search_source", return_value=cands):
        r = await authed_admin_client.post(
            "/api/ingest-sources/search",
            json={"q": "best set", "source": "youtube"},
        )
    assert r.status_code == 200, r.text
    items = {c["external_id"]: c for c in r.json()["items"]}
    assert items["known1"]["already_in_library"] is True
    assert items["new2"]["already_in_library"] is False


@pytest.mark.asyncio
async def test_admin_can_list_and_toggle_sources(authed_admin_client):
    r = await authed_admin_client.get("/api/admin/ingest-sources")
    assert r.status_code == 200, r.text
    assert any(s["kind"] == "youtube" for s in r.json()["items"])
    r2 = await authed_admin_client.put(
        "/api/admin/ingest-sources/youtube", json={"enabled": False}
    )
    assert r2.status_code == 200 and r2.json()["enabled"] is False
