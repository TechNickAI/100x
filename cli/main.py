"""Main CLI entry point for 100x commands."""

import click

from cli.agents import agents


@click.group()
@click.version_option(version="0.1.0", prog_name="100x")
def cli():
    """100x - AI agent system for amplifying human potential."""


# Register command groups
cli.add_command(agents)


if __name__ == "__main__":
    cli()
