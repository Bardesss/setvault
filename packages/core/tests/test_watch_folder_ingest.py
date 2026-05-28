"""Tests for the filename-parser inside watch_folder_ingest.

End-to-end ingest behavior (probe → place → pipeline → unmatched-fallback)
is integration territory and gets covered by the apps/web API + Playwright
tests in 5C. The filename parser is pure logic and worth a dedicated unit
sweep.
"""
from __future__ import annotations

from datetime import date

import pytest
from setvault_core.jobs.watch_folder_ingest import _parse_filename


@pytest.mark.parametrize(("stem", "expected"), [
    # Explicit date + artist + title
    (
        "2026-01-15 - Carl Cox - Awakenings Closing Set",
        {"date": date(2026, 1, 15), "artist": "Carl Cox", "title": "Awakenings Closing Set"},
    ),
    # Alt-date format (dots) and no dash before artist
    (
        "2026.01.15 Carl Cox - Awakenings",
        {"date": date(2026, 1, 15), "artist": "Carl Cox", "title": "Awakenings"},
    ),
    # No date — fall through to bare artist - title
    (
        "Carl Cox - Awakenings Closing Set",
        {"artist": "Carl Cox", "title": "Awakenings Closing Set"},
    ),
    # Em-dash separator (U+2013 — the parser matches both ASCII - and Unicode -)
    (
        "Carl Cox – Awakenings",  # noqa: RUF001
        {"artist": "Carl Cox", "title": "Awakenings"},
    ),
    # Excess whitespace
    (
        "  Carl Cox  -  Awakenings  ",
        {"artist": "Carl Cox", "title": "Awakenings"},
    ),
])
def test_parse_filename_known_patterns(stem: str, expected: dict):
    result = _parse_filename(stem)
    assert result is not None, f"expected a parse for {stem!r}"
    for k, v in expected.items():
        assert result.get(k) == v, f"key {k}: got {result.get(k)!r}, want {v!r}"


@pytest.mark.parametrize("stem", [
    # The parser intentionally treats ANY dashed string as artist-title
    # (admin fixes the metadata on the resulting draft). These cases lack
    # both a date prefix AND any dash, so they fall through to None and
    # land in the unmatched inbox.
    "no_separator_at_all",
    "noseparatoratall",
    "",
    "   ",
    "OnlyOneName",
])
def test_parse_filename_no_pattern(stem: str):
    assert _parse_filename(stem) is None


def test_parse_filename_invalid_date_falls_back():
    """A date-shaped prefix with an impossible date (month 13) should still
    parse via the no-date pattern."""
    stem = "2026-13-99 - Carl Cox - Awakenings"
    result = _parse_filename(stem)
    # The third no-date pattern matches whatever's after the bad-date prefix.
    # Artist token becomes everything before the LAST dash.
    assert result is not None
    assert result.get("title") == "Awakenings"
    # Date must NOT be set when the prefix was invalid
    assert "date" not in result
