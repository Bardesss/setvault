from __future__ import annotations

import re
import unicodedata

_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = _SLUG_NON_ALNUM.sub("-", norm.lower()).strip("-")
    return slug or "item"
