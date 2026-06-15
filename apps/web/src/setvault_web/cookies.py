from __future__ import annotations

import os

from .config import get_settings


def cookie_secure() -> bool:
    """The cookie ``Secure`` attribute, derived from the ``BASE_URL`` scheme so
    it can't drift from the origin the app is actually served on:

      * ``https://…`` → Secure **on** (internet-exposed behind TLS).
      * ``http://…``  → Secure **off**. A Secure cookie is silently dropped by
        the browser on a plain-HTTP origin, so VPN/LAN-only deployments must run
        without it — login would otherwise return 200 but never persist.

    ``SETVAULT_ALLOW_INSECURE_COOKIE=1`` remains an explicit force-off override
    for unusual setups (e.g. a TLS-terminating proxy that the app only ever
    sees over HTTP). It can only relax the flag, never tighten it.

    Single source of truth shared by the auth, invites, and CSRF code paths so
    they can't drift out of sync.
    """
    if os.environ.get("SETVAULT_ALLOW_INSECURE_COOKIE", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return get_settings().base_url.lower().startswith("https://")
