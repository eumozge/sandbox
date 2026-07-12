import logging

import aio_pika
import aio_pika.abc
from domain.api.publishers import TradePagePublisher
from domain.types import Page
from settings import RabbitMQ

logger = logging.getLogger(__name__)


class RabbitMQTradePagePublisher(TradePagePublisher):
    def __init__(self, settings: RabbitMQ) -> None:
        self.settings = settings
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.exchange: aio_pika.abc.AbstractExchange | None = None

    async def setup(self) -> None:
        logger.info("Connecting to RabbitMQ at %s", self.settings.host)
        self.connection = await aio_pika.connect_robust(self.settings.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "spimex",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        queue = await self.channel.declare_queue("spimex.pages", durable=True)
        await queue.bind(self.exchange, routing_key="page.fetched")

    async def publish(self, page: Page) -> None:
        if self.exchange is None:
            logger.warning("Publisher not set up, skipping page %s", page.pid)
            return
        message = aio_pika.Message(
            body=page.to_json().encode(),
            content_type="application/json",
            headers={"page_id": page.pid, "status": str(page.status)},
        )
        await self.exchange.publish(message, routing_key="page.fetched")
        logger.info("Published page %s to RabbitMQ", page.pid)

    async def teardown(self) -> None:
        if self.connection is not None:
            await self.connection.close()
        self.exchange = None
        self.channel = None
        self.connection = None
