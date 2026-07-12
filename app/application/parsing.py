import logging

from domain.api.consumers import TradePageConsumer
from domain.api.parsers import TradePageParser
from domain.types import Page

logger = logging.getLogger(__name__)


class ParseTradesUseCase:
    def __init__(self, consumer: TradePageConsumer, parser: TradePageParser) -> None:
        self.consumer = consumer
        self.parser = parser

    async def handle(self, page: Page) -> None:
        await self.parser.parse(page)

    async def start(self) -> None:
        logger.info("Start parsing trades")
        await self.consumer.setup()
        try:
            await self.consumer.consume(self.handle)
        finally:
            await self.consumer.teardown()
        logger.info("Finished parsing trades")
