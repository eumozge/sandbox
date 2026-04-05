import logging
from typing import Any

import httpx
from domain.api.pages import TradeRepository
from domain.types import Page
from settings import Spimex

logger = logging.getLogger(__name__)


class SpimexPageRepository(TradeRepository):
    def __init__(self, settings: Spimex) -> None:
        self.url = settings.url
        self.session = httpx.AsyncClient()

    async def setup(self) -> None:
        pass

    async def teardown(self) -> None:
        await self.session.aclose()

    async def get(self, pid: str, params: dict[str, Any]) -> Page | None:
        try:
            response = await self.session.get(self.url, params=params)
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Failed to fetch page %s:", pid)
            return None
        else:
            return Page(pid=pid, body=response.text, status=response.status_code)

    async def get_page(self, num: int) -> Page | None:
        params = {"page": f"-{num}"}
        return await self.get(str(num), params)

    async def get_index(self) -> Page | None:
        return await self.get("index", {})
