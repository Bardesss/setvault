import pytest
from setvault_core.services import ingest_sources as svc


@pytest.mark.asyncio
async def test_ensure_seed_states_creates_rows_for_known_kinds(session):
    await svc.ensure_seed_states(session)
    states = await svc.list_states(session)
    assert any(s.kind == "youtube" for s in states)


@pytest.mark.asyncio
async def test_search_success_resets_failures(session, monkeypatch):
    await svc.ensure_seed_states(session)
    from setvault_ingest_sources.base import Candidate

    class _Src:
        kind = "youtube"
        name = "YouTube"

        def search(self, q, *, limit=20):
            return [Candidate("youtube", "v1", "T", "U", 60, None, "https://youtu.be/v1")]

    monkeypatch.setattr(svc, "get_source", lambda kind: _Src())

    cands = await svc.search_source(session, kind="youtube", query="x", limit=5)
    assert cands[0].external_id == "v1"
    st = await svc.get_state(session, "youtube")
    assert st.consecutive_failures == 0 and st.state == "healthy"


@pytest.mark.asyncio
async def test_search_failures_auto_disable_after_threshold(session, monkeypatch):
    await svc.ensure_seed_states(session)
    from setvault_ingest_sources.base import SourceError

    class _BadSrc:
        kind = "youtube"
        name = "YouTube"

        def search(self, q, *, limit=20):
            raise SourceError("nope")

    monkeypatch.setattr(svc, "get_source", lambda kind: _BadSrc())

    for _ in range(svc.AUTO_DISABLE_AFTER):
        with pytest.raises(SourceError):
            await svc.search_source(session, kind="youtube", query="x")
    st = await svc.get_state(session, "youtube")
    assert st.enabled is False and st.state == "auto_disabled"


@pytest.mark.asyncio
async def test_search_disabled_source_raises(session, monkeypatch):
    await svc.ensure_seed_states(session)
    await svc.set_enabled(session, "youtube", False)
    with pytest.raises(svc.SourceDisabledError):
        await svc.search_source(session, kind="youtube", query="x")


@pytest.mark.asyncio
async def test_search_seeds_states_on_first_run(session, monkeypatch):
    # No ensure_seed_states() call — simulate a fresh DB where search is hit first.
    from setvault_ingest_sources.base import Candidate

    class _Src:
        kind = "youtube"
        name = "YouTube"

        def search(self, q, *, limit=20):
            return [Candidate("youtube", "v1", "T", "U", 60, None, "https://youtu.be/v1")]

    monkeypatch.setattr(svc, "get_source", lambda kind: _Src())

    cands = await svc.search_source(session, kind="youtube", query="x", limit=5)
    assert cands[0].external_id == "v1"
    st = await svc.get_state(session, "youtube")
    assert st is not None and st.enabled is True
