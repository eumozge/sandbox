import logging

from domain.api.parsers import TradePageParser
from domain.types import Page

logger = logging.getLogger(__name__)


class StubTradePageParser(TradePageParser):
    async def parse(self, page: Page) -> Page:
        logger.info("Stub parsing page %s (%s bytes)", page.pid, len(page.body))
        return page
