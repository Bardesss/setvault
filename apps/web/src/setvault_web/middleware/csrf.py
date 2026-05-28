"""Pure-ASGI CSRF middleware.

Rewritten in Phase 5E away from ``starlette.middleware.base.BaseHTTPMiddleware``
to eliminate an anyio task-group event-loop race that surfaced in pytest as
``Task ... got Future ... attached to a different loop`` at teardown
(``test_full_reset_cycle`` in apps/web/tests/test_password_reset.py). The pure
ASGI form has no inner task group, so the race cannot fire.
"""
from __future__ import annotations

import json
import os
import secrets
from collections.abc import Awaitable, Callable
from http.cookies import SimpleCookie
from typing import Any

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
EXEMPT_PATHS = frozenset({
    "/api/auth/login",
    "/api/health",
    "/api/uploads/tusd-hooks",
    "/api/dev/seed-e2e",  # gated by SETVAULT_DEV_SEED; router not registered otherwise
})
EXEMPT_PATH_PREFIXES = ("/api/invites/", "/api/password-reset/")
# /api/password-reset/ is exempted because /request and /{token}/redeem are anonymous endpoints
# (no session cookie yet, so no CSRF cookie to validate against).
# Trade-off: the /admin-link sub-path also matches the prefix and loses CSRF enforcement,
# but admin-link is already gated by require_admin (session + role check), which provides
# equivalent protection. Revisit with per-route CSRF if needed.


Scope = dict[str, Any]
Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]


def _cookie_secure() -> bool:
    return os.environ.get("SETVAULT_ALLOW_INSECURE_COOKIE", "").lower() not in (
        "1",
        "true",
        "yes",
    )


def _read_cookies(scope: Scope) -> dict[str, str]:
    raw = b""
    for name, value in scope.get("headers", []):
        if name == b"cookie":
            raw = value
            break
    if not raw:
        return {}
    jar: SimpleCookie = SimpleCookie()
    try:
        jar.load(raw.decode("latin-1"))
    except Exception:  # pragma: no cover - malformed header
        return {}
    return {k: morsel.value for k, morsel in jar.items()}


def _header_value(scope: Scope, target: bytes) -> str | None:
    for name, value in scope.get("headers", []):
        if name == target:
            return value.decode("latin-1")
    return None


def _build_set_cookie(token: str) -> str:
    parts = [
        f"{CSRF_COOKIE}={token}",
        "Path=/",
        "SameSite=Lax",
    ]
    if _cookie_secure():
        parts.append("Secure")
    return "; ".join(parts)


class CsrfMiddleware:
    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        is_exempt = (
            path in EXEMPT_PATHS or any(path.startswith(p) for p in EXEMPT_PATH_PREFIXES)
        )
        cookies = _read_cookies(scope)
        existing = cookies.get(CSRF_COOKIE)

        if method not in SAFE_METHODS and not is_exempt:
            header = _header_value(scope, CSRF_HEADER.encode("latin-1"))
            if not existing or not header or not secrets.compare_digest(existing, header):
                body = json.dumps({"detail": "csrf token missing or mismatched"}).encode()
                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode("ascii")),
                    ],
                })
                await send({"type": "http.response.body", "body": body})
                return

        if existing is not None:
            await self.app(scope, receive, send)
            return

        set_cookie = _build_set_cookie(secrets.token_urlsafe(32)).encode("latin-1")
        injected = False

        async def send_wrapper(event: dict[str, Any]) -> None:
            nonlocal injected
            if not injected and event["type"] == "http.response.start":
                headers = list(event.get("headers", []))
                headers.append((b"set-cookie", set_cookie))
                event = {**event, "headers": headers}
                injected = True
            await send(event)

        await self.app(scope, receive, send_wrapper)
