"""Short-lived HMAC-signed URLs for podcast-enclosure stream access.

Why these exist
---------------
RSS feeds embed an audio enclosure URL for every set. The naive design
threads the user's long-lived ``rss``-scoped ApiToken into every enclosure
URL, which leaks via referer headers, web-server access logs, CDN edge
caches, and browser history - and grants that one token stream access to
*every* set in the catalog, not just the one being enclosed.

The signed-URL approach narrows the blast radius to a single slug and a
short TTL (default 24h). When a podcast app re-polls the feed it gets fresh
signatures; stale enclosures simply 401 and force a refetch.

Wire-format
-----------
``?sig=<base64url-sha256-hmac>&exp=<unix-epoch>``

The signature commits to ``slug + ":" + exp`` using HMAC-SHA256 over the
app's secret key. Verification is constant-time.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime

DEFAULT_ENCLOSURE_TTL_SECONDS = 24 * 3600


def _now() -> int:
    return int(datetime.now(UTC).timestamp())


def sign_stream_url(
    *, secret_key: str, slug: str, exp: int | None = None,
    ttl_seconds: int = DEFAULT_ENCLOSURE_TTL_SECONDS,
) -> tuple[str, int]:
    """Return ``(sig, exp)`` for the given slug.

    ``exp`` is a unix-epoch seconds value; if not supplied it is now+ttl.
    The returned sig is URL-safe base64 with no padding.
    """
    if exp is None:
        exp = _now() + int(ttl_seconds)
    msg = f"{slug}:{exp}".encode("ascii")
    digest = hmac.new(secret_key.encode("ascii"), msg, hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return sig, exp


def verify_stream_sig(
    *, secret_key: str, slug: str, exp: int, sig: str,
) -> bool:
    """Constant-time verification.

    Fails closed on: stale ``exp``, signature mismatch, malformed input.
    Never raises - the caller maps a False to 401.
    """
    if not sig or not slug:
        return False
    if exp < _now():
        return False
    expected, _ = sign_stream_url(secret_key=secret_key, slug=slug, exp=exp)
    return hmac.compare_digest(expected, sig)
