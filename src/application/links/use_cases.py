from domain.links.entities import Link
from domain.links.repositories import LinkRepository
from domain.links.value_objects.short_code import ShortCode


class GetLinkByShortCodeUseCase:
    def __init__(self, repository: LinkRepository) -> None:
        self.repository = repository

    async def execute(self, short_code: str) -> Link | None:
        return await self.repository.get_by_short_code(ShortCode(short_code))
