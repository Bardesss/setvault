import pytest
from setvault_core.services import ingest_sources as svc


@pytest.mark.asyncio
async def test_search_source_raises_when_rate_limited(session, monkeypatch):
    await svc.ensure_seed_states(session)

    async def _deny(*a, **k):
        return False
    monkeypatch.setattr(svc, "_source_allow", _deny)

    with pytest.raises(svc.SourceRateLimitedError):
        await svc.search_source(session, kind="youtube", query="x", limit=5)


@pytest.mark.asyncio
async def test_seeded_states_have_default_limits(session):
    await svc.ensure_seed_states(session)
    st = await svc.get_state(session, "youtube")
    assert st.rate_limit_max == 30
    assert st.rate_limit_window_seconds == 60
