import uuid

import pytest
from setvault_core.models.identity import User
from setvault_core.models.monitors import Monitor, MonitorDiscovery
from setvault_core.services import discoveries as svc
from setvault_core.services.passwords import hash_password
from setvault_ingest_sources.base import Candidate
from sqlalchemy import select


async def _make_user(session):
    u = User(
        email=f"u-{uuid.uuid4().hex[:6]}@x.test",
        username=f"u{uuid.uuid4().hex[:6]}",
        display_name="u",
        password_hash=hash_password("aaaaaaaa"),
    )
    session.add(u)
    await session.flush()
    return u


def _cand(ext_id, title, uploader, kind="soundcloud"):
    return Candidate(
        source_kind=kind,
        external_id=ext_id,
        title=title,
        uploader=uploader,
        duration_seconds=3600,
        thumbnail_url=None,
        webpage_url=f"https://soundcloud.com/x/{ext_id}",
    )


@pytest.mark.asyncio
async def test_process_splits_auto_vs_review_and_caps(session, monkeypatch):
    ripped = []

    async def fake_ingest(s, *, monitor, candidate):
        ripped.append(candidate.external_id)
        return None

    notified = []

    async def fake_notify(s, *, user_id, monitor, summary):
        notified.append(summary)

    monkeypatch.setattr(svc, "_ingest_candidate", fake_ingest)
    monkeypatch.setattr(svc, "_notify_owner", fake_notify)

    u = await _make_user(session)
    m = Monitor(kind="query", query_text="Bicep", owner_user_id=u.id, enabled=True, per_poll_cap=1)
    session.add(m)
    await session.flush()

    cands = [
        _cand("a", "Bicep at Field Day", "Bicep"),   # high
        _cand("b", "Bicep live", "Bicep"),            # high but over cap -> review
        _cand("c", "Random mix", "DJ Nobody"),        # low -> review
    ]
    summary = await svc.process_candidates(session, monitor=m, candidates=cands)
    assert summary["auto_ingested"] == 1
    assert summary["pending_review"] == 2
    assert ripped == ["a"]
    rows = (
        await session.execute(
            select(MonitorDiscovery).where(MonitorDiscovery.monitor_id == m.id)
        )
    ).scalars().all()
    assert len(rows) == 3
    assert notified and notified[0]["auto_ingested"] == 1


@pytest.mark.asyncio
async def test_process_dedups_existing_discoveries(session, monkeypatch):
    async def _none(*a, **k):
        return None

    monkeypatch.setattr(svc, "_ingest_candidate", _none)
    monkeypatch.setattr(svc, "_notify_owner", _none)

    u = await _make_user(session)
    m = Monitor(kind="query", query_text="Bicep", owner_user_id=u.id, enabled=True, per_poll_cap=5)
    session.add(m)
    await session.flush()
    session.add(
        MonitorDiscovery(
            monitor_id=m.id,
            source_kind="soundcloud",
            external_id="a",
            title="x",
            uploader="Bicep",
            webpage_url="u",
            confidence="high",
            status="auto_ingested",
        )
    )
    await session.flush()

    summary = await svc.process_candidates(
        session, monitor=m, candidates=[_cand("a", "Bicep", "Bicep")]
    )
    assert summary["auto_ingested"] == 0
    assert summary["pending_review"] == 0
    assert summary["skipped_duplicate"] == 1


@pytest.mark.asyncio
async def test_entity_monitor_always_high(session, monkeypatch):
    ripped = []

    async def fake_ingest(s, *, monitor, candidate):
        ripped.append(candidate.external_id)
        return None

    async def _none(*a, **k):
        return None

    monkeypatch.setattr(svc, "_ingest_candidate", fake_ingest)
    monkeypatch.setattr(svc, "_notify_owner", _none)

    u = await _make_user(session)
    m = Monitor(
        kind="entity",
        source_kind="soundcloud",
        external_id="chan1",
        owner_user_id=u.id,
        enabled=True,
        per_poll_cap=5,
    )
    session.add(m)
    await session.flush()
    # uploader/title don't match any query, but entity monitors are always high -> auto-ingested
    summary = await svc.process_candidates(
        session, monitor=m, candidates=[_cand("z", "anything", "whoever")]
    )
    assert summary["auto_ingested"] == 1
    assert ripped == ["z"]
