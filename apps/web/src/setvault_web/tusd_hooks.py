"""Helpers for the tusd hook receiver.

Keeps libmagic-dependent code (``sniff_mime``) lazy-imported so this module is
importable on dev machines (notably Windows) where libmagic is not installed.
Production / CI images ship ``libmagic1``.
"""
from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path

from redis import Redis
from rq import Queue

from setvault_web.config import get_settings

_redis: Redis | None = None
_queue: Queue | None = None


def queue() -> Queue:
    """Return a process-wide RQ ``Queue`` bound to the configured Redis URL.

    Lazy so module import does not require a live Redis connection.
    """
    global _redis, _queue
    if _queue is None:
        _redis = Redis.from_url(get_settings().redis_url)
        _queue = Queue("default", connection=_redis)
    return _queue


ALLOWED_MIMES = {
    "audio/flac",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
    "audio/opus",
    "audio/mp4",
    "audio/aac",
    "audio/x-m4a",
}
_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = _SLUG_RE.sub("-", norm.lower()).strip("-")
    return slug or "set"


def normalize_filename(raw: str) -> str:
    raw = unicodedata.normalize("NFC", raw)
    raw = "".join(c for c in raw if c.isprintable())
    base = Path(raw).name
    if not base or ".." in base or base.startswith("."):
        raise ValueError(f"invalid filename: {raw!r}")
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if Path(base).stem.upper() in reserved:
        raise ValueError(f"reserved filename: {raw!r}")
    return base


def sniff_mime(path: Path) -> str:
    """Detect the MIME type of ``path`` via libmagic.

    Import is lazy so dev machines without libmagic can still import this
    module — only callers of ``sniff_mime`` need the library installed.
    """
    import magic

    return magic.from_file(str(path), mime=True) or "application/octet-stream"


def hardlink_or_copy(src: Path, dest: Path) -> None:
    """Move bytes from tusd's temp location into the MediaRoot.

    Hardlink when the filesystem supports it (same device, POSIX); fall back to
    ``copy2`` otherwise (cross-device, Windows, network mounts).
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.hardlink_to(src)
    except (OSError, NotImplementedError):
        shutil.copy2(src, dest)
