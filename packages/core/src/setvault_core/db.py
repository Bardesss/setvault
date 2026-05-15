from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

_engine: AsyncEngine | None = None
_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(url: str) -> AsyncEngine:
    global _engine, _factory
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
