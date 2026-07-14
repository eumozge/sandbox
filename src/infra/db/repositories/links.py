from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.links import entities, value_objects as vo
from domain.links.repositories import LinkRepository
from infra.db.models.links import LINKS_TABLE


class SQLLinkRepository(LinkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_short_code(self, short_code: vo.ShortCode) -> entities.Link | None:
        stmt = select(entities.Link).where(LINKS_TABLE.c.short_code == short_code.value)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_link(self, link: entities.Link) -> entities.Link:
        self.session.add(link)
        await self.session.flush()
        return link
