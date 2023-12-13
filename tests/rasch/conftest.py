import json
import re
from collections import defaultdict
from typing import Any

import pytest
import yaml
from clingo.control import Control

from rasch.file import read_from_pickle_file
from rasch.logging import get_logger
from rasch.rasch_config import RaSchConfig
from rasch.rasch_solver import RaSchSolver


@pytest.fixture(scope="session")
def test_config() -> RaSchConfig:
    with open('tests/rasch/environments/test_config.yaml', 'r') as config_file:
        data: dict[str, Any] = yaml.safe_load(config_file)

        if "rasch_config" not in data:
            raise (EOFError("Reached end of file before rasch_config was declared."))

        if not isinstance(data["rasch_config"], RaSchConfig):
            raise (TypeError("config.yaml is not correctly formatted"))

        return data["rasch_config"]


@pytest.fixture(scope="session")
def json_simple_switch_map_from_pkl(test_config):
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
    solver.solve(encoding_name,f"{encoding_name}_{environment_name}_instance")

    solve_file = f"{encoding_name}_{environment_name}_solve.json"
    solver.save(solve_file)

    with open(f"{test_config.solver_output_path}{solve_file}") as json_data:
        data = json.load(json_data)

    yield data


@pytest.fixture(scope="session")
def json_simple_switch_map_from_instance(test_config):
    logger = get_logger()

    # [encoding, environment to test] #TODO: variable
    args = ["dev", "simple_switch_map"]

    encoding_name = args[0]
    environment_name = args[1]

    clingo_control = Control()
    solver = RaSchSolver(clingo_control=clingo_control,
                         logger=logger,
                         config=test_config
                         )
    solver.solve(encoding_name,f"{encoding_name}_{environment_name}_instance")

    solve_file = f"{encoding_name}_{environment_name}_solve.json"
    solver.save(solve_file)

    with open(f"{test_config.solver_output_path}{solve_file}") as json_data:
        data = json.load(json_data)

    yield data

@pytest.fixture(scope="session")
def get_trans_unsorted(json_simple_switch_map_from_instance):
    first_model = json_simple_switch_map_from_instance["models"][0]
    pattern0 = re.compile(r'trans\(0,[^\"]*') #matches every trans from agent0 until "
    pattern1 = re.compile(r'trans\(1,[^\"]*')
    list0 = []
    list1 = []
    dict_trans_unsorted = defaultdict(dict_safe_function)

    for entry in first_model:
        if re.findall(pattern0,entry): #find trans of agent 0
            list0.append(entry)        #and append to list
        if re.findall(pattern1,entry): #find trans of agent 1
            list1.append(entry)

    dict_trans_unsorted[0] = list0 #agent 0 transitions
    dict_trans_unsorted[1] = list1 #agent 1 transitions

    yield dict_trans_unsorted

def dict_safe_function():
    return False
