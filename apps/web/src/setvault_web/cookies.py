from __future__ import annotations

import os


def cookie_secure() -> bool:
    """The cookie ``Secure`` attribute. True by default; opt out only via
    ``SETVAULT_ALLOW_INSECURE_COOKIE`` for local HTTP-only development/e2e
    (Playwright over http://localhost). Never disable in production — over plain
    HTTP the browser will silently drop the session cookie.

    Single source of truth shared by the auth, invites, and CSRF code paths so
    they can't drift out of sync.
    """
    return os.environ.get("SETVAULT_ALLOW_INSECURE_COOKIE", "").lower() not in (
        "1",
        "true",
        "yes",
    )
