from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware


CSP = (
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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", CSP)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=(), usb=()"
        )
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        return response
