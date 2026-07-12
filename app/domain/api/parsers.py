import abc

from domain.types import Page


class TradePageParser(abc.ABC):
    @abc.abstractmethod
    async def parse(self, page: Page) -> Page: ...
