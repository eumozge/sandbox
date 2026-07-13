from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import orjson
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@asynccontextmanager
async def get_engine(url: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        url,
        echo=False,
        json_serizlier=lambda val: orjson.dumps(val).decode(),
        json_deserilizer=orjson.loads,
        pool_size=50,
    )
    yield engine
    await engine.dispose()


def get_sessing_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_sessin(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
