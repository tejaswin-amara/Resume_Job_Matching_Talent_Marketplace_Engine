import asyncio
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url).replace("@localhost:", "@127.0.0.1:")

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_timeout=30.0,
    echo=False,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_engine_cache: dict[asyncio.AbstractEventLoop, async_sessionmaker[AsyncSession]] = {}


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _engine_cache, async_session_maker
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return async_session_maker

    if loop not in _engine_cache:
        eng = create_async_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_timeout=30.0,
            echo=False,
        )
        _engine_cache[loop] = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)

    return _engine_cache[loop]


async def get_db_session() -> AsyncSession:
    maker = get_sessionmaker()
    async with maker() as session:
        yield session
