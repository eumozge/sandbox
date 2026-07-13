from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.links.entities import Link
from domain.links.repositories import LinkRepository
from domain.links.value_objects.url import URL
from infra.db.models.links import LINKS_TABLE


class SQLLinkRepository(LinkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_original(self, original: URL) -> Link | None:
        stmt = select(Link).where(LINKS_TABLE.c.original == original.value)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
