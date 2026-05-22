"""1001tracklists scraper — admin-gated, rate-limited.

ToS-grey: 1001tracklists prohibits automated access. This module is fenced by
SETVAULT_ALLOW_1001TL_SCRAPE in the API layer; admins opt in per deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

ALLOWED_HOSTS = {"www.1001tracklists.com", "1001tracklists.com"}
UA = "SetVault/0.1 (+https://github.com/Bardesss/setvault) personal-use"


@dataclass
class Scraped:
    start_seconds: int | None
    raw_label: str


class HostRejected(ValueError):
    pass


class FetchFailed(RuntimeError):
    pass


def _parse_cue(cue: str | None) -> int | None:
    if not cue:
        return None
    parts = cue.strip().split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        return None
    return None


async def scrape_1001tracklists(url: str, *, timeout_s: float = 15.0) -> list[Scraped]:
    host = urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        raise HostRejected(f"host not allowed: {host}")
    async with httpx.AsyncClient(timeout=timeout_s, headers={"User-Agent": UA}) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise FetchFailed(f"upstream {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    out: list[Scraped] = []
    for item in soup.select("div.tlpItem"):
        cue_el = item.select_one(".cueValueField")
        cue = cue_el.get("data-cue") if cue_el else None
        label_el = item.select_one(".trackValue")
        label = label_el.get_text(strip=True) if label_el else ""
        if not label:
            continue
        out.append(Scraped(start_seconds=_parse_cue(cue), raw_label=label))
    return out
