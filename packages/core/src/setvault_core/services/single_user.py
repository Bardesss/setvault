"""Single-user auto-login.

When the ``single_user_auto_login`` system setting is on AND exactly one active
user exists, the app authenticates as that sole user without a login page. The
double gate (explicit opt-in + exactly-one-user) keeps a multi-user instance
from ever silently dropping auth, and the admin toggle itself is refused unless
the single-user condition holds (see api/admin.py).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.identity import User
from setvault_core.services.system_config import get_config


def should_auto_login(*, enabled: bool, active_user_count: int) -> bool:
    """Pure decision: auto-login only when enabled and there is exactly one
    active user."""
    return enabled and active_user_count == 1


async def single_user_auto_login_candidate(session: AsyncSession) -> User | None:
    """Return the sole active user to auto-authenticate as, or ``None`` when
    auto-login does not apply."""
    config = await get_config(session)
    active = (
        await session.execute(
            select(User).where(User.disabled_at.is_(None))
        )
    ).scalars().all()
    if not should_auto_login(
        enabled=config.single_user_auto_login, active_user_count=len(active)
    ):
        return None
    return active[0]
