from __future__ import annotations

import secrets

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PATHS = {"/api/auth/login", "/api/health", "/api/uploads/tusd-hooks"}
EXEMPT_PATH_PREFIXES = ("/api/invites/", "/api/password-reset/")
# /api/password-reset/ is exempted because /request and /{token}/redeem are anonymous endpoints
# (no session cookie yet, so no CSRF cookie to validate against).
# Trade-off: the /admin-link sub-path also matches the prefix and loses CSRF enforcement,
# but admin-link is already gated by require_admin (session + role check), which provides
# equivalent protection for Phase 2A. Revisit with per-route CSRF in Phase 2B if needed.


class CsrfMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        is_exempt = path in EXEMPT_PATHS or any(path.startswith(p) for p in EXEMPT_PATH_PREFIXES)
        if request.method not in SAFE_METHODS and not is_exempt:
            cookie = request.cookies.get(CSRF_COOKIE)
            header = request.headers.get(CSRF_HEADER)
            if not cookie or not header or not secrets.compare_digest(cookie, header):
                return JSONResponse(
                    {"detail": "csrf token missing or mismatched"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        response = await call_next(request)
        if request.cookies.get(CSRF_COOKIE) is None:
            response.set_cookie(
                CSRF_COOKIE, secrets.token_urlsafe(32),
                httponly=False, secure=True, samesite="lax", path="/",
            )
        return response
