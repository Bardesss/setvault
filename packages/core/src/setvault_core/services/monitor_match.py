"""Deterministic confidence scoring for monitor discoveries.

A candidate is `high` confidence iff every normalized token of the monitor
query is present as a whole word in the candidate's uploader OR title.
Entity-follow monitors are always high (the caller passes confidence directly).
No fuzzy/ML matching — intentionally simple and unit-testable.
"""
from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_tokens(text: str | None) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def score_confidence(query: str, *, uploader: str | None, title: str | None) -> str:
    query_tokens = normalize_tokens(query)
    if not query_tokens:
        return "low"
    uploader_set = set(normalize_tokens(uploader))
    title_set = set(normalize_tokens(title))
    if all(t in uploader_set for t in query_tokens):
        return "high"
    if all(t in title_set for t in query_tokens):
        return "high"
    return "low"
