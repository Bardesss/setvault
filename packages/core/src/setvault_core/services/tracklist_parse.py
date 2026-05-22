"""Pure regex parser for pasted tracklist text. No DB, no I/O — pure function."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedEntry:
    start_seconds: int | None
    raw_label: str


# Anchored at line start, allows leading whitespace, then either:
#   HH:MM:SS or MM:SS  (timestamp form)
#   N. or N)           (numbered form, no timestamp)
# Followed by the label.
_TIMESTAMP = re.compile(
    r"^\s*"
    r"(?:(?P<h>\d{1,2}):)?"
    r"(?P<m>\d{1,2}):"
    r"(?P<s>\d{2})"
    r"\s+(?P<label>.+?)\s*$"
)
_NUMBERED = re.compile(r"^\s*(?P<n>\d{1,3})[.)]\s+(?P<label>.+?)\s*$")
# Lines that look like artist - title without timestamp/number.
_FALLBACK = re.compile(r"^\s*(?P<label>[^\d].+?\s+-\s+.+?)\s*$")
# Headers / separators / metadata.
_SKIP = re.compile(r"^\s*(?:tracklist:?|---+|===+|\d+\s*tracks?)\s*$", re.IGNORECASE)


def parse_tracklist_text(text: str) -> list[ParsedEntry]:
    if not text or not text.strip():
        return []
    out: list[ParsedEntry] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or _SKIP.match(line):
            continue
        m = _TIMESTAMP.match(line)
        if m:
            h = int(m.group("h") or 0)
            mm = int(m.group("m"))
            ss = int(m.group("s"))
            out.append(ParsedEntry(start_seconds=h * 3600 + mm * 60 + ss,
                                   raw_label=m.group("label")))
            continue
        m = _NUMBERED.match(line)
        if m:
            out.append(ParsedEntry(start_seconds=None, raw_label=m.group("label")))
            continue
        m = _FALLBACK.match(line)
        if m:
            out.append(ParsedEntry(start_seconds=None, raw_label=m.group("label")))
    return out
