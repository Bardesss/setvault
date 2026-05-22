from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.tracklist import TracklistEntry


class InvalidPosition(ValueError):
    pass


async def list_entries(session: AsyncSession, live_set_id: uuid.UUID) -> list[TracklistEntry]:
    return list((await session.execute(
        select(TracklistEntry).where(TracklistEntry.live_set_id == live_set_id)
        .order_by(TracklistEntry.position)
    )).scalars().all())


async def create_entry(
    session: AsyncSession,
    live_set_id: uuid.UUID,
    *,
    user_id: uuid.UUID,
    start_seconds: int,
    raw_label: str,
    position: int | None = None,
    end_seconds: int | None = None,
    edit_notes: str | None = None,
) -> TracklistEntry:
    existing = await list_entries(session, live_set_id)
    pos = position if position is not None else len(existing)
    if pos < 0 or pos > len(existing):
        raise InvalidPosition(f"position {pos} outside [0, {len(existing)}]")
    # Shift everything at pos.. +1
    for e in existing:
        if e.position >= pos:
            e.position += 1
    entry = TracklistEntry(
        live_set_id=live_set_id,
        position=pos,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        raw_label=raw_label,
        edit_notes=edit_notes,
        created_by=user_id,
    )
    session.add(entry)
    await session.flush()
    return entry


async def update_entry(
    session: AsyncSession,
    entry: TracklistEntry,
    *,
    start_seconds: int | None = None,
    end_seconds: int | None = None,
    raw_label: str | None = None,
    edit_notes: str | None = None,
    mashup_with: list[uuid.UUID] | None = None,
) -> TracklistEntry:
    if start_seconds is not None:
        entry.start_seconds = start_seconds
    if end_seconds is not None:
        entry.end_seconds = end_seconds
    if raw_label is not None:
        entry.raw_label = raw_label
    if edit_notes is not None:
        entry.edit_notes = edit_notes
    if mashup_with is not None:
        entry.mashup_with = mashup_with
    await session.flush()
    return entry


async def delete_entry(session: AsyncSession, entry: TracklistEntry) -> None:
    live_set_id = entry.live_set_id
    deleted_position = entry.position
    await session.delete(entry)
    await session.flush()
    # Collapse positions above the deleted one
    remaining = await list_entries(session, live_set_id)
    for r in remaining:
        if r.position > deleted_position:
            r.position -= 1


async def reorder_entries(
    session: AsyncSession,
    live_set_id: uuid.UUID,
    *,
    entry_id: str,
    after_position: int,
) -> None:
    """Move `entry_id` so that its new position is right after `after_position`.

    after_position == -1 means move to position 0 (start of list).
    """
    entries = await list_entries(session, live_set_id)
    n = len(entries)
    if after_position < -1 or after_position >= n:
        raise InvalidPosition(f"after_position {after_position} not in [-1, {n - 1}]")
    target = next((e for e in entries if str(e.id) == entry_id), None)
    if target is None:
        raise InvalidPosition(f"entry {entry_id} not in set")
    new_pos = after_position + 1 if target.position > after_position else after_position
    if target.position == new_pos:
        return
    # Renumber all entries with the target removed conceptually
    others = [e for e in entries if e.id != target.id]
    others.insert(new_pos, target)
    for i, e in enumerate(others):
        e.position = i
    await session.flush()


async def time_shift_entries(
    session: AsyncSession,
    live_set_id: uuid.UUID,
    *,
    after_seconds: int,
    delta_seconds: int,
) -> int:
    """Shift start_seconds (and end_seconds where set) of entries with
    start_seconds > after_seconds by delta_seconds. Clamps at 0.

    Returns the number of rows touched.
    """
    entries = await list_entries(session, live_set_id)
    count = 0
    for e in entries:
        if e.start_seconds > after_seconds:
            e.start_seconds = max(0, e.start_seconds + delta_seconds)
            if e.end_seconds is not None:
                e.end_seconds = max(0, e.end_seconds + delta_seconds)
            count += 1
    await session.flush()
    return count
