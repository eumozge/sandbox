from abc import ABC, abstractmethod

from domain.links.entities import Link
from domain.links.value_objects.url import URL


class LinkRepository(ABC):
    @abstractmethod
    async def get_by_original(self, original: URL) -> Link | None: ...
