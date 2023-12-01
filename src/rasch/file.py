import os

from flatland.envs.persistence import RailEnvPersister
from flatland.envs.rail_env import RailEnv

from rasch.rasch_config import get_config


def create_path_if_not_exist(*, path: str) -> None:
    """ Create the specified path if it does not exist already."""
    does_exist = os.path.exists(path=path)
    if not does_exist:
        os.makedirs(path)


def write_lines_to_file(*, path: str, file_name: str, lines: list[str]) -> None:
    """ Write given list of lines to specified file in path.

        The path is created if it does not exist.
    """
    create_path_if_not_exist(path=path)
    file_path = os.path.join(path, file_name)

    with open(file_path, 'w') as f:
        f.writelines(f'{line}\n' for line in lines)


def read_from_pickle_file(file_name: str, path: str = get_config().flatland_environments_path) -> RailEnv:
    """ Read Flatland environment from pickle file."""
    file_path = os.path.join(path, file_name)
    env, _ = RailEnvPersister.load_new(filename=file_path)

    return env


def save_as_pickle_file(file_name: str,
                        env: RailEnv, path: str = get_config().flatland_environments_path):
    """ Saves the provided Flatland environment as a pickle file in the specified path.

        The path is created if it does not exist.
    """
    create_path_if_not_exist(path=path)
    file_path = os.path.join(path, file_name)

    RailEnvPersister.save(env=env, filename=file_path)
