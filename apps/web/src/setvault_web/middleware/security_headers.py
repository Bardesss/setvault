"""Pure-ASGI security-headers middleware.

Rewritten in Phase 5E away from ``starlette.middleware.base.BaseHTTPMiddleware``
for the same reason as the CSRF middleware: BaseHTTPMiddleware's inner anyio
task group leaks across pytest event loops and breaks the test harness even
though production paths work. The pure ASGI form has no inner task group.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

# Default CSP for the app: blocks framing entirely.
_DEFAULT_CSP = (
    "default-src 'self'; "
    "img-src 'self' data: blob:; "
    "media-src 'self' blob:; "
    "font-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

# CSP for embeddable routes: same as default but allows any parent frame.
_EMBED_CSP = (
    "default-src 'self'; "
    "img-src 'self' data: blob:; "
    "media-src 'self' blob:; "
    "font-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self' ws: wss:; "
    "frame-ancestors *; "
    "base-uri 'self'; "
    "form-action 'self'"
)

# Public CSP for stream/waveform asset endpoints that an embedded page loads
# from a third-party origin. The browser only enforces frame-ancestors against
# documents, not media; we leave their CSP unchanged but skip X-Frame-Options
# so the parent page can still frame the wider /embed/ page.
CSP = _DEFAULT_CSP  # exported for tests/legacy importers

_DEFAULTS = (
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), usb=()"),
    (
        b"strict-transport-security",
        b"max-age=63072000; includeSubDomains; preload",
    ),
)


Scope = dict[str, Any]
Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]


def _is_embed_route(path: str) -> bool:
    """Routes that need third-party iframe embedding to work.

    Frontend page: ``/embed/<slug>``.
    Backend JSON used by that page: ``/api/sets/<slug>/embed``.
    """
    if path.startswith("/embed/") or path == "/embed":
        return True
    if path.startswith("/api/sets/") and path.endswith("/embed"):
        return True
    return False


def _setdefault(headers: list[tuple[bytes, bytes]], name: bytes, value: bytes) -> None:
    for existing_name, _ in headers:
        if existing_name == name:
            return
    headers.append((name, value))


class SecurityHeadersMiddleware:
    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        embed = _is_embed_route(scope.get("path", "/"))
        csp = _EMBED_CSP if embed else _DEFAULT_CSP

        async def send_wrapper(event: dict[str, Any]) -> None:
            if event["type"] == "http.response.start":
                headers = list(event.get("headers", []))
                _setdefault(headers, b"content-security-policy", csp.encode("latin-1"))
                if not embed:
                    _setdefault(headers, b"x-frame-options", b"DENY")
                for name, value in _DEFAULTS:
                    _setdefault(headers, name, value)
                event = {**event, "headers": headers}
            await send(event)

        await self.app(scope, receive, send_wrapper)
