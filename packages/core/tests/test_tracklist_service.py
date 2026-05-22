import pytest
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.services.tracklist import (
    InvalidPosition,
    reorder_entries,
    time_shift_entries,
)
from sqlalchemy import select


@pytest.mark.asyncio
async def test_reorder_to_end(session_with_set):
    session, live_id, entry_ids = session_with_set
    # entry_ids is [a, b, c] at positions 0, 1, 2 — move a to position 2
    await reorder_entries(session, live_id, entry_id=entry_ids[0], after_position=2)
    rows = await _entries_ordered(session, live_id)
    assert [str(r.id) for r in rows] == [entry_ids[1], entry_ids[2], entry_ids[0]]


@pytest.mark.asyncio
async def test_reorder_to_start(session_with_set):
    session, live_id, entry_ids = session_with_set
    # move c (pos 2) to first
    await reorder_entries(session, live_id, entry_id=entry_ids[2], after_position=-1)
    rows = await _entries_ordered(session, live_id)
    assert [str(r.id) for r in rows] == [entry_ids[2], entry_ids[0], entry_ids[1]]


@pytest.mark.asyncio
async def test_reorder_rejects_bad_position(session_with_set):
    session, live_id, entry_ids = session_with_set
    with pytest.raises(InvalidPosition):
        await reorder_entries(session, live_id, entry_id=entry_ids[0], after_position=99)


@pytest.mark.asyncio
async def test_time_shift_positive(session_with_set):
    session, live_id, _ = session_with_set
    # Entries at start_seconds [0, 60, 120] — shift those > 30s by +10
    count = await time_shift_entries(session, live_id, after_seconds=30, delta_seconds=10)
    assert count == 2
    rows = await _entries_ordered(session, live_id)
    assert [r.start_seconds for r in rows] == [0, 70, 130]


@pytest.mark.asyncio
async def test_time_shift_negative_clamps_to_zero(session_with_set):
    session, live_id, _ = session_with_set
    # Shift entries > 0 by -100 — must clamp at 0
    await time_shift_entries(session, live_id, after_seconds=0, delta_seconds=-100)
    rows = await _entries_ordered(session, live_id)
    assert all(r.start_seconds >= 0 for r in rows)


async def _entries_ordered(session, live_id):
    return (await session.execute(
        select(TracklistEntry).where(TracklistEntry.live_set_id == live_id)
        .order_by(TracklistEntry.position)
    )).scalars().all()
