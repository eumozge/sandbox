import logging

import click
from presentation.cli.trades import trades

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


if __name__ == "__main__":
    logger.info("Starting application")
    cli.add_command(trades)
    cli()
