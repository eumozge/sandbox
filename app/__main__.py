import click
from presentation.cli.trades import trades


@click.group()
def cli() -> None:
    pass


if __name__ == "__main__":
    cli.add_command(trades)
    cli()
