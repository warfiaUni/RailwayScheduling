from functools import lru_cache
from typing import Any

import yaml


class RaSchConfig(yaml.YAMLObject):
    default_encoding: str
    default_environment: str
    asp_encodings_path: str
    asp_instances_path: str
    flatland_environments_path: str
    solver_output_path: str
    statistics_output_path:str

    yaml_tag: str = '!config'
    yaml_loader = yaml.SafeLoader


@lru_cache
def get_config() -> RaSchConfig:
    with open('config.yaml', 'r') as config_file:
        data: dict[str, Any] = yaml.safe_load(config_file)

        if "rasch_config" not in data:
            raise (EOFError("Reached end of file before rasch_config was declared."))

        if not isinstance(data["rasch_config"], RaSchConfig):
            raise (TypeError("config.yaml is not correctly formatted"))

        return data["rasch_config"]

@lru_cache
def get_horizons(key):
    with open('config.yaml', 'r') as config_file:
        data: dict[str, Any] = yaml.safe_load(config_file)

        if "rasch_horizon" not in data:
            raise (EOFError("Reached end of file before rasch_horizon was declared."))

        if key not in data["rasch_horizon"]:
            print("Found no horizon for environment.")
            return -1 #TODO
            raise (EOFError(f"rasch_horizon in config.yaml does not have key: {key}"))
        
        return data["rasch_horizon"][key]