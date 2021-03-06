"""
Scripting
"""
import datetime
import json
import logging
from pathlib import Path

import click
from cmdstanpy import CmdStanModel

from src.generate_data import DataGenerator
from src.encoder import NumpyEncoder

logging.basicConfig(format="[%(asctime)s] %(levelname)s - %(message)s")
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
    datagen.to_json(Path(config_path))  # round-trip in case we regenerated true params
    exogs, endo = datagen.simulate()

    output_path = Path(
        output_pattern.format(
            name=datagen.name,
            version=datagen.version,
            timestamp=f"{datetime.datetime.now():%Y%m%d%H%M}",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Writing exog and endo to %s", output_path)

    # reindex interaction info to be 1-indexed
    interaction_indexes = [
        [x + 1 for x in row] for row in datagen.true_params["interaction"].keys()
    ]

    with open(output_path, "w") as output_file:
        json.dump(
            dict(
                N=exogs.shape[0],
                M=exogs.shape[1],
                c=1,
                m0=datagen.num_strong_effects,
                X=exogs.tolist(),
                y=endo.tolist(),
                I=datagen.num_interactions,
                interaction_levels=datagen.num_interaction_levels,
                interaction_indexes=interaction_indexes,
            ),
            fp=output_file,
            cls=NumpyEncoder,
        )


@cli.command()
@click.option("--model-path", required=True, type=str, help="Path to stan model")
@click.option("--data-path", required=True, type=str, help="Path to data")
@click.option(
    "--sample-path", default="output", type=str, help="Path to output HMC samples"
)
def fit(model_path, data_path, sample_path):
    """fit a model using cmdstanpy"""
    model_path = Path(model_path)
    data_path = Path(data_path)
    timestamp = f"{datetime.datetime.now():%Y%m%d%H%M}"
    output_path = Path(sample_path) / f"{model_path.stem}-{data_path.stem}-{timestamp}"
    output_path.mkdir(parents=True, exist_ok=True)

    model = CmdStanModel(stan_file=model_path)
    logger.info("Fitting %s using %s", data_path.stem, model_path.stem)
    fit = model.sample(
        data=str(data_path),
        show_console=True,
        output_dir=output_path,
        chains=4,
        iter_warmup=1000,
        iter_sampling=1000,
    )
    logger.info(fit.summary())


if __name__ == "__main__":
    cli()
    logger.info("Done")
