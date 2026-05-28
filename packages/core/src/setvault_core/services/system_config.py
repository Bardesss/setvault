"""Singleton config service. Migration `0013_5b` seeds the row at upgrade
time so the getter never has to handle a missing row in production; the
``get_or_create`` fallback is a belt-and-suspenders for fresh test DBs
where alembic hasn't run yet."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.system_config import SystemConfig


async def get_config(session: AsyncSession) -> SystemConfig:
    row = (await session.execute(
        select(SystemConfig).where(SystemConfig.singleton.is_(True))
    )).scalar_one_or_none()
    if row is not None:
        return row
    row = SystemConfig(singleton=True)
    session.add(row)
    await session.flush()
    return row
