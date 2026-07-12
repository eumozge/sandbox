import asyncio

import click
from application.trades import CollectTradesUseCase
from infra.api.pages import SpimexPageRepository
from infra.api.publishers import RabbitMQTradePagePublisher
from settings import rabbitmq, spimex


@click.group(name="trades")
def trades() -> None: ...


@trades.command()
@click.option("--to-page", default=500, type=int, help="Last page number to collect")
def collect(to_page: int) -> None:
    repo = SpimexPageRepository(settings=spimex)
    publisher = RabbitMQTradePagePublisher(settings=rabbitmq)
    use_case = CollectTradesUseCase(repository=repo, publisher=publisher)
    asyncio.run(use_case.start(from_page=1, to_page=to_page))
