import abc
from collections.abc import Awaitable, Callable

from domain.types import Page

type PageHandler = Callable[[Page], Awaitable[None]]


class TradePageConsumer(abc.ABC):
    @abc.abstractmethod
    async def setup(self) -> None: ...

    @abc.abstractmethod
    async def consume(self, handler: PageHandler) -> None: ...

    @abc.abstractmethod
    async def teardown(self) -> None: ...
