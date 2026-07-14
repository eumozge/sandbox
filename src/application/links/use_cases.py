from domain.links import entities, value_objects as vo
from domain.links.repositories import LinkRepository


class GetLinkByShortCodeUseCase:
    def __init__(self, repository: LinkRepository) -> None:
        self.repository = repository

    async def execute(self, short_code: str) -> entities.Link | None:
        return await self.repository.get_by_short_code(vo.ShortCode(short_code))


class CreateLinkUseCase:
    def __init__(self, repository: LinkRepository) -> None:
        self.repository = repository

    async def execute(self, original_url: str, short_code: str) -> entities.Link:
        link = entities.Link(original_url=vo.URL(original_url), short_code=vo.ShortCode(short_code))
        return await self.repository.create_link(link)
