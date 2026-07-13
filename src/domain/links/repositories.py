from abc import ABC, abstractmethod

from domain.links.entities import Link
from domain.links.value_objects.short_code import ShortCode


class LinkRepository(ABC):
    @abstractmethod
    async def get_by_short_code(self, short_code: ShortCode) -> Link | None: ...
