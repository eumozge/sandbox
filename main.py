import abc
import asyncio
import logging
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from enum import StrEnum, auto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_thumbnail(data: bytes) -> bytes:
    time.sleep(1)
    return data[:4] if len(data) > 4 else data


class Connect(abc.ABC):
    @abc.abstractmethod
    def is_ready_to_read(self) -> bool:
        pass

    @abc.abstractmethod
    def is_ready_to_write(self) -> bool:
        pass

    @abc.abstractmethod
    def read(self) -> bytes:
        pass

    @abc.abstractmethod
    def write(self, data: bytes) -> int:
        pass


class ImageType(StrEnum):
    SMALL = auto()
    LARGE = auto()


def image_classifier(image: bytes, image_size: int = 1024 * 1024) -> ImageType:
    return ImageType.SMALL if len(image) < image_size else ImageType.LARGE


class ThumnailProcessor:
    def __init__(
        self,
        *,
        connects: list[Connect],
        image_classifier: Callable[[bytes], ImageType],
        max_queue_size: int = 10,
    ) -> None:
        self.connects = connects
        self.picture_classifier = image_classifier
        self.queues = {t: asyncio.Queue(maxsize=max_queue_size) for t in ImageType}
        self.process_executor = ProcessPoolExecutor()
        self.shutdown = asyncio.Event()
        self.tasks = set()

    async def setup(self) -> None: ...

    async def teardown(self) -> None:
        if self.tasks:
            await asyncio.gather(*self.tasks)

    async def wait(self, connect: Connect, checker: Callable[[Connect], bool]) -> None:
        while True:
            if checker(connect):
                return
            await asyncio.sleep(0.01)

    async def put(self, connect: Connect | None, image: bytes) -> None:
        queue = self.queues[self.picture_classifier(image)]
        await queue.put((connect, image))

    async def generate(self, connect: Connect, image: bytes) -> None:
        logger.info("generate thumbnail for connect %s", connect)
        loop = asyncio.get_event_loop()
        thumbnail = await loop.run_in_executor(self.process_executor, generate_thumbnail, image)
        logger.info("write thumbnail for connect %s", connect)
        await self.wait(connect, checker=lambda x: x.is_ready_to_write())
        connect.write(thumbnail)

    async def produce(self) -> None:
        logger.info("start producer")
        for connect in self.connects:
            await self.wait(connect, checker=lambda x: x.is_ready_to_read())
            image = connect.read()
            await self.put(connect, image)

        logger.info("end consumer")

        for queue in self.queues.values():
            await queue.put((None, None))

    async def consume(self, queue: asyncio.Queue) -> None:
        logger.info("start consumer")
        while True:
            connect, image = await queue.get()
            if connect is None:
                return
            task = asyncio.create_task(self.generate(connect, image))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.remove)

            queue.task_done()

    async def process(self) -> None:
        await self.setup()
        consumers = [self.consume(self.queues[t]) for t in ImageType]
        await asyncio.gather(self.produce(), *consumers)
        await self.teardown()


async def process(connects: list[Connect]) -> None:
    processor = ThumnailProcessor(connects=connects, image_classifier=image_classifier)
    await processor.process()

