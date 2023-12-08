import pytest
import yaml

import json

from clingo.control import Control
from rasch.file import read_from_pickle_file
from rasch.rasch_solver import RaSchSolver
from rasch.logging import get_logger
from rasch.rasch_config import RaSchConfig

#

@pytest.fixture
def test_config():       #TODO: tmp_path
    with open("tests/rasch/environments/hierBinIch.txt","w") as f:
        f.write("Hallo")
    with open("tests/rasch/environments/test_config.yaml","r") as yaml_data:
        yaml_config = yaml.dump(yaml_data)
    yield yaml_config

@pytest.fixture
def json_simple_switch_map(test_config):
    logger = get_logger()
    args = ["dev","simple_switch_map"] #[encoding, environment to test] #TODO: variable

    encoding_name = args[0]
    environment_name = args[1]
    env = read_from_pickle_file(f'tests/rasch/environments/{environment_name}.pkl')
    env.reset()

    clingo_control = Control()
    solver = RaSchSolver(environment=env,
                            clingo_control=clingo_control,
                            logger=logger,
                            config=RaSchConfig(test_config)
                            )
    solver.solve(encoding_name)

    solve_file = f"{encoding_name}_{environment_name}_solve.json"
    solver.save(solve_file)

    with open(solve_file) as json_data:
        data = json.load(json_data)

    yield data