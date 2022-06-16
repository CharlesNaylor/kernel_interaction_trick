"""
Scripting
"""
import datetime
import json
import logging
from pathlib import Path

import click

from src.generate_data import DataGenerator

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@cli.command()
@click.option(
    "--config_path",
    required=True,
    type=str,
    help="Path to serialized data generation config",
)
def generate_data(
    config_path: str, output_pattern: str = "data/{name}_{version}_{timestamp}.json"
):
    """generates data for use in the SKIM experiments"""
    datagen = DataGenerator.from_json(Path(config_path))
    exogs, endo = datagen.simulate()

    output_path = Path(
        output_pattern.format(
            name=datagen.name,
            version=datagen.version,
            timestamp=f"{datetime.datetime.now():%Y%m%d%H%M}",
        )
    )
    logger.info("Writing exog and endo to %s", output_path)
    with open(output_path, "w") as output_file:
        json.dump(dict(X=exogs.tolist(), y=endo.tolist()), fp=output_file)


if __name__ == "__main__":
    cli()
    logger.info("Done")
