import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from itertools import chain
from typing import TypeVar

T = TypeVar("T")
CommitTag = TypeVar("CommitTag")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Batch[T, CommitTag]:
    items: list[T] = field(default_factory=list)
    commit_tag: CommitTag | None = None

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(len(self))


class Producer[T, CommitTag](ABC):
    @abstractmethod
    async def next(self) -> Batch[T, CommitTag]: ...

    @abstractmethod
    async def commit(self, commit_tag: CommitTag) -> None: ...


class Consumer[T](ABC):
    MAX_ITEMS = 1000

    @abstractmethod
    async def process(self, items: list[T]) -> None: ...


class PipeProcessor[T, CommitTag]:
    def __init__(
        self, producer: Producer[T, CommitTag], consumer: Consumer[T], max_queue_size: int = 10
    ) -> None:
        self.producer = producer
        self.consumer = consumer
        self.queue: asyncio.Queue[Batch[T, CommitTag]] = asyncio.Queue(maxsize=max_queue_size)
        self.storage: list[Batch[T, CommitTag]] = []
        self.storage_items_size = 0

    async def flush(self) -> None:
        if not self.storage:
            return
        items = list(chain.from_iterable(b.items for b in self.storage))

        await self.consumer.process(items)
        tags = [b.commit_tag for b in self.storage if b.commit_tag is not None]
        async with asyncio.TaskGroup() as group:
            for tag in tags:
                group.create_task(self.producer.commit(tag))
        self.reset_storage()

    def update_storage(self, batch: Batch[T, CommitTag]) -> None:
        self.storage.append(batch)
        self.storage_items_size += len(batch)

    def reset_storage(self) -> None:
        self.storage = []
        self.storage_items_size = 0

    async def produce(self) -> None:
        while True:
            try:
                batch = await self.producer.next()
            except Exception:
                await self.queue.put(Batch())
                logger.exception("Producer failed with:")
                return

            await self.queue.put(batch)
            if not batch:
                return

    async def consume(self) -> None:
        while True:
            try:
                batch = await self.queue.get()
                if not batch:
                    break

                if self.storage and self.storage_items_size + len(batch) >= self.consumer.MAX_ITEMS:
                    await self.flush()

            except asyncio.CancelledError:
                logger.warning("Consumer was canceled.")
                return

            self.update_storage(batch)

        await self.flush()

    async def setup(self) -> None: ...

    async def teardown(self) -> None: ...

    async def pipe(self) -> None:
        await self.setup()
        async with asyncio.TaskGroup() as group:
            group.create_task(self.produce())
            group.create_task(self.consume())
        await self.teardown()
