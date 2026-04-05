import asyncio
import logging

from domain.api.pages import TradeRepository
from domain.types import Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectTradesUseCase:
    def __init__(
        self,
        repository: TradeRepository,
        simultaneously: int = 3,
    ) -> None:
        self.repository = repository
        self.queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=3)
        self.semaphore = asyncio.Semaphore(simultaneously)
        self.active_tasks: set[asyncio.Task[Page | None]] = set()

    async def fetch(self, page_num: int) -> Page | None:
        async with self.semaphore:
            page = await self.repository.get_page(page_num)
            if page is None:
                return None
            return page

    def fetch_done_callback(self, task: asyncio.Task) -> None:
        self.active_tasks.discard(task)
        self.queue.task_done()

    async def consume(self) -> None:
        while page_num := await self.queue.get():
            task = asyncio.create_task(self.fetch(page_num))
            self.active_tasks.add(task)
            task.add_done_callback(self.fetch_done_callback)
            self.queue.task_done()

    async def produce(self, from_page: int, to_page: int) -> None:
        for page in range(from_page, to_page + 1):
            await self.queue.put(page)
        await self.queue.put(None)

    async def start(self, from_page: int = 0, to_page: int = 0) -> None:
        logger.info("Start collect trades from %s to %s", from_page, to_page)
        await self.repository.setup()
        await asyncio.gather(self.produce(from_page, to_page), self.consume())
        await self.queue.join()
        await self.repository.setup()
