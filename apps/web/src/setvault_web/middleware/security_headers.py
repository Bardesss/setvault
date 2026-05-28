from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        embed = _is_embed_route(request.url.path)
        response.headers.setdefault(
            "Content-Security-Policy", _EMBED_CSP if embed else _DEFAULT_CSP,
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        # Embed routes must NOT carry X-Frame-Options (the legacy header would
        # block even the CSP-permitted frame).
        if not embed:
            response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=(), usb=()"
        )
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=63072000; includeSubDomains; preload",
        )
        return response
