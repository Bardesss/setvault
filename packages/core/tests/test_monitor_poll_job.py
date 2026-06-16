import uuid

import pytest
from setvault_core.jobs import monitor_poll as job
from setvault_core.models.identity import User
from setvault_core.models.monitors import Monitor
from setvault_core.services import ingest_sources as ingest_svc
from setvault_core.services.passwords import hash_password
from setvault_ingest_sources.base import Candidate


async def _make_user(session):
    u = User(email=f"u-{uuid.uuid4().hex[:6]}@x.test", username=f"u{uuid.uuid4().hex[:6]}",
             display_name="u", password_hash=hash_password("aaaaaaaa"))
    session.add(u)
    await session.flush()
    return u


def _cand(ext_id):
    return Candidate(source_kind="soundcloud", external_id=ext_id, title="t",
                     uploader="u", duration_seconds=1, thumbnail_url=None,
                     webpage_url=f"https://x/{ext_id}")


@pytest.mark.asyncio
async def test_poll_query_monitor_calls_search_all_and_processes(session, monkeypatch):
    u = await _make_user(session)
    m = Monitor(kind="query", query_text="Bicep", owner_user_id=u.id, enabled=True, per_poll_cap=5)
    session.add(m)
    await session.flush()

    async def fake_search_all(s, *, query, limit_per_source=10):
        return ingest_svc.SearchAllResult(candidates=[_cand("a")], errored_kinds=[])
    captured = {}
    async def fake_process(s, *, monitor, candidates):
        captured["count"] = len(candidates)
        return {"auto_ingested": 1, "pending_review": 0, "skipped_duplicate": 0}
    monkeypatch.setattr(job, "search_all_sources", fake_search_all)
    monkeypatch.setattr(job, "process_candidates", fake_process)

    summary = await job.poll_monitor(session, monitor_id=m.id)
    assert captured["count"] == 1
    assert summary["auto_ingested"] == 1
    refreshed = await session.get(Monitor, m.id)
    assert refreshed.last_checked_at is not None


@pytest.mark.asyncio
async def test_poll_entity_monitor_calls_single_source(session, monkeypatch):
    u = await _make_user(session)
    m = Monitor(kind="entity", source_kind="soundcloud", external_id="chan1",
                owner_user_id=u.id, enabled=True, per_poll_cap=5)
    session.add(m)
    await session.flush()

    called = {}
    async def fake_search_source(s, *, kind, query, limit=20):
        called["kind"] = kind
        return [_cand("a")]
    async def fake_process(s, *, monitor, candidates):
        return {"auto_ingested": 0, "pending_review": 1, "skipped_duplicate": 0}
    monkeypatch.setattr(job, "search_source", fake_search_source)
    monkeypatch.setattr(job, "process_candidates", fake_process)

    await job.poll_monitor(session, monitor_id=m.id)
    assert called["kind"] == "soundcloud"


@pytest.mark.asyncio
async def test_poll_swallows_rate_limit(session, monkeypatch):
    u = await _make_user(session)
    m = Monitor(kind="query", query_text="x", source_kind="youtube",
                owner_user_id=u.id, enabled=True, per_poll_cap=5)
    session.add(m)
    await session.flush()

    async def boom(s, *, kind, query, limit=20):
        raise ingest_svc.SourceRateLimitedError(kind)
    processed = {}
    async def fake_process(s, *, monitor, candidates):
        processed["count"] = len(candidates)
        return {"auto_ingested": 0, "pending_review": 0, "skipped_duplicate": 0}
    monkeypatch.setattr(job, "search_source", boom)
    monkeypatch.setattr(job, "process_candidates", fake_process)

    await job.poll_monitor(session, monitor_id=m.id)  # must not raise
    assert processed["count"] == 0
