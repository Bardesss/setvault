from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

_engine: AsyncEngine | None = None
_factory: async_sessionmaker[AsyncSession] | None = None


def _nullpool_enabled() -> bool:
    return os.environ.get("SETVAULT_DB_NULLPOOL", "").lower() in ("1", "true", "yes")


def init_engine(url: str) -> AsyncEngine:
    global _engine, _factory
    if _nullpool_enabled():
        # Test suites create many short-lived engines (the web conftest calls
        # init_engine in ~17 autouse fixtures per test). A real pool leaves idle
        # asyncpg connections lingering, exhausting Postgres's max_connections on
        # CI. NullPool opens/closes a connection per use and sidesteps asyncio
        # event-loop binding — the same strategy the core test fixtures use.
        _engine = create_async_engine(url, poolclass=NullPool, future=True)
    else:
        _engine = create_async_engine(url, pool_pre_ping=True, future=True)
    _factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine


def engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Engine not initialized — call init_engine() first")
    return _engine


def session_factory() -> async_sessionmaker[AsyncSession]:
    if _factory is None:
        raise RuntimeError("Engine not initialized — call init_engine() first")
    return _factory
