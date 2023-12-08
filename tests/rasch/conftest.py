import json

import pytest
import yaml
from clingo.control import Control

from rasch.file import read_from_pickle_file
from rasch.logging import get_logger
from rasch.rasch_config import RaSchConfig
from rasch.rasch_solver import RaSchSolver


@pytest.fixture
def test_config() -> RaSchConfig:
    with open('tests/rasch/environments/test_config.yaml', 'r') as config_file:
        data: dict[str, Any] = yaml.safe_load(config_file)

        if "rasch_config" not in data:
            raise (EOFError("Reached end of file before rasch_config was declared."))

        if not isinstance(data["rasch_config"], RaSchConfig):
            raise (TypeError("config.yaml is not correctly formatted"))

        return data["rasch_config"]


@pytest.fixture
def json_simple_switch_map(test_config):
    logger = get_logger()

    # [encoding, environment to test] #TODO: variable
    args = ["dev", "simple_switch_map"]

    encoding_name = args[0]
    environment_name = args[1]
    env = read_from_pickle_file(
        f'{environment_name}.pkl', path=test_config.flatland_environments_path)
    env.reset()

    clingo_control = Control()
    solver = RaSchSolver(environment=env,
                         clingo_control=clingo_control,
                         logger=logger,
                         config=test_config
                         )
    solver.solve(encoding_name)

    solve_file = f"{encoding_name}_{environment_name}_solve.json"
    solver.save(solve_file)

    with open(f"{test_config.solver_output_path}{solve_file}") as json_data:
        data = json.load(json_data)

    yield data
