import json
import logging

import aio_pika
import aio_pika.abc
from domain.api.consumers import PageHandler, TradePageConsumer
from domain.types import Page
from settings import RabbitMQ

logger = logging.getLogger(__name__)


class RabbitMQTradePageConsumer(TradePageConsumer):
    def __init__(self, settings: RabbitMQ) -> None:
        self.settings = settings
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None

    async def setup(self) -> None:
        logger.info("Connecting to RabbitMQ at %s", self.settings.host)
        self.connection = await aio_pika.connect_robust(self.settings.url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("spimex.pages", durable=True)

    async def consume(self, handler: PageHandler) -> None:
        assert self.queue is not None
        async with self.queue.iterator() as queue:
            async for message in queue:
                async with message.process():
                    body = json.loads(message.body.decode())
                    page = Page.from_json(body)
                    await handler(page)

    async def teardown(self) -> None:
        assert self.connection is not None
        await self.connection.close()
        self.channel = None
        self.queue = None
        self.connection = None
