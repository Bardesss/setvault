from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta


def generate_token() -> tuple[str, str]:
    """Returns (plaintext_url_token, sha256_hash). Store the hash; deliver the plaintext."""
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    return token, digest


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def expires(hours: int) -> datetime:
    return datetime.now(UTC) + timedelta(hours=hours)


def now_utc() -> datetime:
    return datetime.now(UTC)
