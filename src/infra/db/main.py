from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import orjson
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infra.settings import PostgresSettings


@asynccontextmanager
async def get_engine(settings: PostgresSettings) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        str(settings.dsn),
        echo=False,
        json_serizlier=lambda val: orjson.dumps(val).decode(),
        json_deserilizer=orjson.loads,
        pool_size=50,
    )
    yield engine
    await engine.dispose()


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
