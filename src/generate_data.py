"""
Generate fake data for testing
We want a set of exogs with random parameters we will recover
"""
import ast
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from src.encoder import NumpyEncoder

logger = logging.getLogger(__name__)


@dataclass
class DataGenerator:
    """
    Tracking hierarchical simulation parameters

    :param num_strong_effects: how many exogs have significant coefficients?
    :param num_interaction_levels: to what degree should we have interactions?
    e.g. 2 = B_i*B_j, 3 = B_i*B_j*B_k
    :param error_scale: if y ~ normal(B'X, sigma), this is sigma
    """

    name: str = ""
    version: str = "0.1"
    num_obs: int = 1000
    num_strong_effects: int = None
    num_exogs: int = 10
    num_interaction_levels: int = 2
    num_interactions: int = None
    error_scale: float = 1
    true_params: Dict[List[int], float] = None

    def __post_init__(self):
        if self.num_strong_effects is None:
            self.num_strong_effects = self.num_exogs // self.num_interaction_levels
        assert self.num_strong_effects <= self.num_exogs
        assert self.num_strong_effects > 0

        if self.num_interactions is None:
            self.num_interactions = (
                self.num_strong_effects // self.num_interaction_levels
            )

        # must have enough strong effects to also have interactions
        # interactions are restricted by skim algo to exist on strong effects
        assert (
            self.num_interactions * self.num_interaction_levels
        ) <= self.num_strong_effects

        if self.true_params is None:
            self.true_params = self.generate_true_params()

    @classmethod
    def from_json(cls, json_path: Path):
        """instantiate from saved json file"""
        with open(Path(json_path), "r") as json_file:
            params = json.load(json_file)
        if params.get("true_params", False):
            for x in ["single", "interaction"]:
                params["true_params"][x] = {
                    ast.literal_eval(k): v for k, v in params["true_params"][x].items()
                }
        return cls(**params)

    def to_json(self, json_path: Path):
        """save to json"""
        params = asdict(self)
        for x in ["single", "interaction"]:
            params["true_params"][x] = {
                str(k): v for k, v in params["true_params"][x].items()
            }
        with open(Path(json_path), "w") as json_file:
            json.dump(params, fp=json_file, cls=NumpyEncoder)
            logger.info("Wrote data generator configuration to %s", Path(json_path))

    def generate_true_params(self):
        """create some random true parameters to recover based on configuration"""

        # Get the first order effects
        strong_effects = (
            np.ceil(np.random.standard_normal(self.num_strong_effects) * 1000) / 100
        )  # effective sigma of 10

        indexes = np.random.choice(
            self.num_exogs, self.num_strong_effects, replace=False
        )
        # get interactions
        # note assumption that interactions only happen on strong effects
        interactions = np.random.choice(
            indexes.shape[0],
            (self.num_interactions, self.num_interaction_levels),
            replace=False,
        )
        # switch to true exog indexes
        interaction_indexes = np.vectorize(lambda x: indexes[x])(interactions)

        interaction_effects = (
            np.ceil(np.random.standard_normal(self.num_interactions) * 1000) / 100
        )

        # put indexes in as a list b/c the rest will be interactions
        true_params = {
            "single": dict(zip([(i,) for i in indexes], strong_effects)),
        }

        true_params["interaction"] = dict(
            zip(map(tuple, interaction_indexes), interaction_effects.tolist())
        )

        return true_params

    def simulate(self):
        """generate data from the config"""
        exogs = np.random.standard_normal(size=(self.num_obs, self.num_exogs))
        interacted_exogs = np.zeros(shape=(self.num_obs, self.num_interactions))

        base_coefs = np.zeros(self.num_exogs)
        for index, coef in self.true_params["single"].items():
            base_coefs[index[0]] = coef

        for i, (index, coef) in enumerate(self.true_params["interaction"].items()):
            interacted_exogs[:, i] = exogs[:, index].prod(axis=1) * coef
        endo = (
            exogs.dot(base_coefs)
            + interacted_exogs.sum(axis=1)
            + self.error_scale * np.random.standard_normal(size=self.num_obs)
        )
        logger.info(
            "Generated exogs and endo using data generator %s, version %s",
            self.name,
            self.version,
        )
        return exogs, endo
