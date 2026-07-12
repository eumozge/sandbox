import abc

from domain.types import Page


class TradePagePublisher(abc.ABC):
    @abc.abstractmethod
    async def setup(self) -> None: ...

    @abc.abstractmethod
    async def publish(self, page: Page) -> None: ...

    @abc.abstractmethod
    async def teardown(self) -> None: ...
