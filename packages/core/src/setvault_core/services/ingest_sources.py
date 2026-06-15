from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.ingest_sources import IngestSourceState
from setvault_ingest_sources.base import Candidate, SourceError
from setvault_ingest_sources.registry import all_source_kinds, get_source

AUTO_DISABLE_AFTER = 5


class SourceDisabledError(Exception):
    """The requested source is disabled (manually or auto)."""


async def ensure_seed_states(session: AsyncSession) -> None:
    """Create an IngestSourceState row for every registered source kind that
    doesn't have one yet. Idempotent."""
    existing = {s.kind for s in (await session.execute(select(IngestSourceState))).scalars()}
    for kind in all_source_kinds():
        if kind not in existing:
            session.add(IngestSourceState(kind=kind, enabled=True, state="healthy"))
    await session.flush()


async def list_states(session: AsyncSession) -> list[IngestSourceState]:
    await ensure_seed_states(session)
    return list((await session.execute(
        select(IngestSourceState).order_by(IngestSourceState.kind)
    )).scalars())


async def get_state(session: AsyncSession, kind: str) -> IngestSourceState | None:
    return (await session.execute(
        select(IngestSourceState).where(IngestSourceState.kind == kind)
    )).scalar_one_or_none()


async def set_enabled(session: AsyncSession, kind: str, enabled: bool) -> IngestSourceState:
    st = await get_state(session, kind)
    if st is None:
        st = IngestSourceState(kind=kind)
        session.add(st)
    st.enabled = enabled
    if enabled:
        st.state = "healthy"
        st.consecutive_failures = 0
        st.last_error = None
    else:
        st.state = "manually_disabled"
    await session.flush()
    return st


async def search_source(
    session: AsyncSession, *, kind: str, query: str, limit: int = 20,
) -> list[Candidate]:
    await ensure_seed_states(session)
    st = await get_state(session, kind)
    if st is None or not st.enabled:
        raise SourceDisabledError(kind)
    source = get_source(kind)
    if source is None:
        raise SourceDisabledError(kind)
    try:
        results = source.search(query, limit=limit)
    except SourceError as e:
        st.consecutive_failures += 1
        st.last_error = str(e)[:500]
        if st.consecutive_failures >= AUTO_DISABLE_AFTER:
            st.enabled = False
            st.state = "auto_disabled"
        else:
            st.state = "degraded"
        await session.flush()
        raise
    st.consecutive_failures = 0
    st.state = "healthy"
    st.last_error = None
    await session.flush()
    return results
