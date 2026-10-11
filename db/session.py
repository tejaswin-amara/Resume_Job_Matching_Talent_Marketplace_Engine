import asyncio
import contextlib
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url).replace(
    "@localhost:", "@127.0.0.1:"
)

_engine = None
_session_maker = None
_loop: asyncio.AbstractEventLoop | None = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _engine, _session_maker, _loop
    current_loop: asyncio.AbstractEventLoop | None = None
    with contextlib.suppress(RuntimeError):
        current_loop = asyncio.get_running_loop()

    if _engine is None or (
        _loop is not None and current_loop is not None and _loop is not current_loop
    ):
        if _engine is not None:
            _engine.sync_engine.dispose()
        _engine = create_async_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_timeout=30.0,
            echo=False,
        )
        _session_maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
        _loop = current_loop
    return _session_maker


async def close_db_engine():
    global _engine, _session_maker, _loop
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_maker = None
        _loop = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    maker = get_sessionmaker()
    async with maker() as session:
        yield session
