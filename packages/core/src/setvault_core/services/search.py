from __future__ import annotations

import re

_TOKEN = re.compile(r"[\w-]+", re.UNICODE)


def to_tsquery(raw: str) -> str:
    tokens = _TOKEN.findall(raw)
    if not tokens:
        return ""
    return " & ".join(f"{t}:*" for t in tokens)
