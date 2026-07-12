import asyncio
import logging

from domain.api.pages import TradeRepository
from domain.api.publishers import TradePagePublisher
from domain.types import Page

logger = logging.getLogger(__name__)


class CollectTradesUseCase:
    def __init__(
        self,
        repository: TradeRepository,
        publisher: TradePagePublisher,
        simultaneously: int = 3,
    ) -> None:
        self.repository = repository
        self.publisher = publisher
        self.queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=3)
        self.semaphore = asyncio.Semaphore(simultaneously)
        self.active_tasks: set[asyncio.Task[Page | None]] = set()

    async def fetch(self, page_num: int) -> Page | None:
        async with self.semaphore:
            page = await self.repository.get_page(page_num)
            if page is None:
                return None
            return page

    def fetch_done_callback(self, task: asyncio.Task[Page | None]) -> None:
        page = task.result()
        if page is not None:
            pub_task = asyncio.create_task(self.publisher.publish(page))
            self.active_tasks.add(pub_task)
            pub_task.add_done_callback(self.active_tasks.discard)
        self.active_tasks.discard(task)

    async def consume(self) -> None:
        while page_num := await self.queue.get():
            task = asyncio.create_task(self.fetch(page_num))
            self.active_tasks.add(task)
            task.add_done_callback(self.fetch_done_callback)

    async def produce(self, from_page: int, to_page: int) -> None:
        for page in range(from_page, to_page + 1):
            await self.queue.put(page)
        await self.queue.put(None)

    async def start(self, from_page: int = 1, to_page: int = 1) -> None:
        logger.info("Start collect trades from %s to %s", from_page, to_page)
        await self.repository.setup()
        await self.publisher.setup()
        await asyncio.gather(self.produce(from_page, to_page), self.consume())
        await self.queue.join()
        await self.repository.teardown()
        await self.publisher.teardown()
