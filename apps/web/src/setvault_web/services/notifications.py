"""Web-side ``enqueue_email`` shim that pulls ``redis_url`` from ``Settings``.

The actual implementation lives in ``setvault_core.services.email_dispatch``
so the notification dispatcher in packages/core can reach it without importing
upward.
"""
from __future__ import annotations

from setvault_core.services.email_dispatch import enqueue_email as _core_enqueue_email
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import Settings


async def enqueue_email(
    session: AsyncSession,
    settings: Settings,
    *,
    to: str,
    subject: str,
    text: str,
) -> bool:
    """Enqueue an email via the first enabled SMTP connector.

    Thin wrapper around :func:`setvault_core.services.email_dispatch.enqueue_email`
    that adapts the ``Settings``-based call shape used by ``api/invites.py`` and
    ``api/password_reset.py``. Returns False (without raising) when no SMTP
    connector exists or Redis is unreachable; callers handle that by surfacing
    the copy-paste fallback link in their response.
    """
    return await _core_enqueue_email(
        session, redis_url=settings.redis_url, to=to, subject=subject, text=text,
    )
