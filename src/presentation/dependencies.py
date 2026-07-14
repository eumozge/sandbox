from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.links.use_cases import CreateLinkUseCase, GetLinkByShortCodeUseCase
from infra.db.repositories.links import SQLLinkRepository


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        yield session


async def get_link_by_short_code_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetLinkByShortCodeUseCase:
    repository = SQLLinkRepository(session)
    return GetLinkByShortCodeUseCase(repository)


async def create_link_use_case(
    session: AsyncSession = Depends(get_session),
) -> CreateLinkUseCase:
    repository = SQLLinkRepository(session)
    return CreateLinkUseCase(repository)
