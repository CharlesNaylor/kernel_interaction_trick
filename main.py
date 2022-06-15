"""
Scripting
"""
import datetime
from pathlib import Path

import click

from src.generate_data import DataGenerator


@click.command()
def cli():
    pass


@cli.command()
@cli.option("--config_path", required=True, type=str)
def generate_data(
    config_path: str, output_pattern: str = "data/{name}_{version}_{timestamp}"
):
    """generates data for use in the SKIM experiments"""
    pass


if __name__ == "__main__":
    cli()
