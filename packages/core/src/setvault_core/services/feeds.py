"""Build RSS 2.0 + iTunes podcast feeds from LiveSet rows.

A feed is built per (user, scope) where scope is one of:
  favorites, recent, everything.

Each LiveSet becomes one ``<item>``. TracklistEntries are rendered twice:

  1. As plain text in the item ``<description>`` so any podcast client shows
     the tracklist in show-notes.
  2. As ``<psc:chapters>`` per the Podlove Simple Chapters spec so apps that
     support podcast chapters (Overcast, Pocket Casts, Apple Podcasts, etc.)
     render them as a navigable chapter list.

feedgen's podcast extension doesn't expose PSC, so chapters are injected as a
post-processing pass over feedgen's XML output via lxml.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from feedgen.feed import FeedGenerator
from lxml import etree

from setvault_core.models.catalog import LiveSet
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.services.signed_urls import (
    DEFAULT_ENCLOSURE_TTL_SECONDS,
    sign_stream_url,
)

# Podlove Simple Chapters namespace.
PSC_NS = "http://podlove.org/simple-chapters"


def build_feed(
    *,
    title: str,
    self_link: str,
    description: str,
    items: Iterable[tuple[LiveSet, list[TracklistEntry]]],
    base_url: str,
    signing_key: str,
    enclosure_ttl_seconds: int = DEFAULT_ENCLOSURE_TTL_SECONDS,
) -> bytes:
    """Return UTF-8 XML bytes for the feed.

    Enclosure URLs are HMAC-signed and short-TTL (default 24h). The user's
    long-lived RSS token is *not* embedded in enclosures - it only
    authorizes the feed-XML fetch itself.
    """
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.title(title)
    fg.link(href=self_link, rel="self")
    fg.description(description)
    fg.language("en")
    fg.podcast.itunes_category("Music", "Music Commentary")
    fg.podcast.itunes_explicit("no")

    # Preserve the items as a list so we can correlate them with feedgen's
    # output order when injecting PSC chapters below.
    items_list = list(items)

    for live, entries in items_list:
        fe = fg.add_entry()
        fe.id(f"{base_url}/sets/{live.slug}")
        fe.title(live.title)
        fe.link(href=f"{base_url}/sets/{live.slug}")
        fe.description(_build_description(live, entries))
        sig, exp = sign_stream_url(
            secret_key=signing_key, slug=live.slug,
            ttl_seconds=enclosure_ttl_seconds,
        )
        audio_url = f"{base_url}/api/sets/{live.slug}/stream?sig={sig}&exp={exp}"
        fe.enclosure(url=audio_url, length="0", type="audio/ogg")
        fe.published(_pub_date(live))

    raw = fg.rss_str(pretty=True)
    return _inject_psc_chapters(raw, items_list)


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


def _format_psc_time(seconds: int) -> str:
    """Podlove Simple Chapters: ``HH:MM:SS.mmm`` (millisecond precision)."""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, ss = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{ss:02d}.000"


def _inject_psc_chapters(
    xml: bytes,
    items: list[tuple[LiveSet, list[TracklistEntry]]],
) -> bytes:
    """Walk the feedgen RSS output and add ``<psc:chapters>`` to each ``<item>``.

    feedgen has no first-class PSC support, so we parse its output, add the
    Podlove namespace at the root, and inject one ``<psc:chapter>`` per
    ``TracklistEntry`` row. The input is bytes we just produced ourselves -
    no untrusted XML round-trip, so plain lxml is fine.
    """
    if not items:
        return xml

    parser = etree.XMLParser(no_network=True, resolve_entities=False)
    root = etree.fromstring(xml, parser=parser)
    channel = root.find("channel")
    if channel is None:
        return xml

    item_elems = channel.findall("item")
    for item_elem, (_live, entries) in zip(item_elems, items, strict=False):
        if not entries:
            continue
        chapters = etree.SubElement(
            item_elem,
            f"{{{PSC_NS}}}chapters",
            nsmap={"psc": PSC_NS},
            attrib={"version": "1.2"},
        )
        for ent in entries:
            label = (ent.raw_label or "").strip() or f"Track {ent.position}"
            etree.SubElement(
                chapters,
                f"{{{PSC_NS}}}chapter",
                attrib={
                    "start": _format_psc_time(ent.start_seconds),
                    "title": label,
                },
            )

    return etree.tostring(
        root, pretty_print=True, xml_declaration=True, encoding="utf-8",
    )
