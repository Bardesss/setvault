from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Literal

HealthStatus = Literal["ok", "unreachable", "readonly", "near_full", "unknown"]


def probe(host_path: str, *, near_full_pct: float = 95.0) -> HealthStatus:
    p = Path(host_path)
    if not p.exists():
        return "unreachable"
    if not os.access(p, os.W_OK):
        return "readonly"
    try:
        usage = shutil.disk_usage(p)
    except OSError:
        return "unknown"
    pct = (usage.used / usage.total) * 100 if usage.total else 0
    if pct >= near_full_pct:
        return "near_full"
    return "ok"


def resolve_set_path(host_root: str, relative: str) -> Path:
    root = Path(host_root).resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path {relative!r} escapes media root") from exc
    return candidate
