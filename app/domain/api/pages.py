import abc

from domain.types import Page


class TradeRepository(abc.ABC):
    @abc.abstractmethod
    async def setup(self) -> None: ...

    @abc.abstractmethod
    async def teardown(self) -> None: ...

    @abc.abstractmethod
    async def get_page(self, num: int) -> Page | None: ...

    @abc.abstractmethod
    async def get_index(self) -> Page | None: ...
