from abc import ABC, abstractmethod

import domain.links.value_objects as vo
from domain.links import entities


class LinkRepository(ABC):
    @abstractmethod
    async def get_by_short_code(self, short_code: vo.ShortCode) -> entities.Link | None: ...

    @abstractmethod
    async def create_link(self, link: entities.Link) -> entities.Link: ...
