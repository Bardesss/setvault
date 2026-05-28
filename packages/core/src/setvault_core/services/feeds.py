"""Build RSS 2.0 + iTunes podcast feeds from LiveSet rows.

A feed is built per (user, scope) where scope is one of:
  favorites, recent, everything.

Each LiveSet becomes one <item>. TracklistEntries are rendered in the item
description so any podcast client shows them; native Podlove Simple Chapters
are skipped (feedgen's podcast extension doesn't expose them cleanly, and
description text is universally rendered).
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from feedgen.feed import FeedGenerator

from setvault_core.models.catalog import LiveSet
from setvault_core.models.tracklist import TracklistEntry


def build_feed(
    *,
    title: str,
    self_link: str,
    description: str,
    items: Iterable[tuple[LiveSet, list[TracklistEntry]]],
    base_url: str,
    rss_token: str,
) -> bytes:
    """Return UTF-8 XML bytes for the feed."""
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.title(title)
    fg.link(href=self_link, rel="self")
    fg.description(description)
    fg.language("en")
    fg.podcast.itunes_category("Music", "Music Commentary")
    fg.podcast.itunes_explicit("no")

    for live, entries in items:
        fe = fg.add_entry()
        fe.id(f"{base_url}/sets/{live.slug}")
        fe.title(live.title)
        fe.link(href=f"{base_url}/sets/{live.slug}")
        fe.description(_build_description(live, entries))
        audio_url = f"{base_url}/api/sets/{live.slug}/stream?token={rss_token}"
        fe.enclosure(url=audio_url, length="0", type="audio/ogg")
        fe.published(_pub_date(live))

    return fg.rss_str(pretty=True)


def _build_description(live: LiveSet, entries: list[TracklistEntry]) -> str:
    lines: list[str] = []
    if live.description:
        lines.append(live.description)
        lines.append("")
    if entries:
        lines.append("Tracklist:")
        for ent in entries:
            ts = _format_ts(ent.start_seconds)
            label = (ent.raw_label or "").strip() or f"Track {ent.position}"
            lines.append(f"  {ts}  {label}")
    return "\n".join(lines) or live.title


def _pub_date(live: LiveSet) -> datetime:
    if live.date is not None:
        return datetime(live.date.year, live.date.month, live.date.day, tzinfo=UTC)
    if live.created_at is not None:
        ca = live.created_at
        return ca if ca.tzinfo else ca.replace(tzinfo=UTC)
    return datetime.now(UTC)


def _format_ts(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, ss = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{ss:02d}"
    return f"{m:02d}:{ss:02d}"
