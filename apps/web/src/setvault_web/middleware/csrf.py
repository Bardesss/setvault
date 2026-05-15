from __future__ import annotations

import secrets

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PATHS = {"/api/auth/login", "/api/health", "/api/uploads/tusd-hooks"}


class CsrfMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in SAFE_METHODS and request.url.path not in EXEMPT_PATHS:
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
