from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from defusedxml import ElementTree as ET

from setvault_core.models.catalog import LiveSet
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.services.feeds import build_feed, _format_ts


def _make_live(title: str, slug: str, *, when: date | None = None) -> LiveSet:
    live = LiveSet(
        slug=slug, title=title,
        media_root_id=uuid.uuid4(),
        audio_path="x/y.opus", status="published",
        source_type="upload", uploaded_by=uuid.uuid4(),
        date=when,
    )
    live.created_at = datetime.now(UTC)
    return live


def _make_entry(live_id: uuid.UUID, *, pos: int, sec: int, label: str) -> TracklistEntry:
    return TracklistEntry(
        live_set_id=live_id, position=pos, start_seconds=sec,
        raw_label=label, created_by=uuid.uuid4(),
    )


def test_build_feed_produces_valid_rss():
    live_id = uuid.uuid4()
    live = _make_live("Closing Set", "closing-set", when=date(2026, 1, 15))
    live.id = live_id
    entries = [
        _make_entry(live_id, pos=0, sec=0, label="Track A - Artist X"),
        _make_entry(live_id, pos=1, sec=185, label="Track B - Artist Y"),
    ]
    xml = build_feed(
        title="Test Feed", self_link="https://example/api/feed/recent/T.xml",
        description="desc",
        items=[(live, entries)],
        base_url="https://example", signing_key="test-secret-key-XYZ",
    )
    assert xml.startswith(b"<?xml")
    root = ET.fromstring(xml)
    items = root.findall(".//item")
    assert len(items) == 1
    title = items[0].findtext("title")
    assert title == "Closing Set"
    desc = items[0].findtext("description")
    assert "Track A - Artist X" in desc
    assert "Track B - Artist Y" in desc
    # Enclosure is a signed short-TTL URL — never the raw rss_token.
    enc = items[0].find("enclosure")
    assert enc is not None
    url = enc.attrib["url"]
    assert "stream" in url
    assert "sig=" in url
    assert "exp=" in url
    assert "token=" not in url


def test_build_feed_handles_empty_items():
    xml = build_feed(
        title="Empty Feed", self_link="https://example/x.xml",
        description="d", items=[], base_url="https://example",
        signing_key="test-secret-key-XYZ",
    )
    root = ET.fromstring(xml)
    assert root.findall(".//item") == []


def test_format_ts():
    assert _format_ts(0) == "00:00"
    assert _format_ts(65) == "01:05"
    assert _format_ts(3725) == "01:02:05"
