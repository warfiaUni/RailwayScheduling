import os
from tempfile import TemporaryDirectory

import numpy as np
import pytest
from flatland.core.grid.rail_env_grid import RailEnvTransitions
from flatland.core.transition_map import GridTransitionMap
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import rail_from_grid_transition_map

from rasch.file import (
    create_path_if_not_exist,
    read_from_pickle_file,
    save_as_pickle_file,
    write_lines_to_file,
)


def test_create_path_if_not_exist():
    with TemporaryDirectory() as temp_dir:
        # Create a path that does not exist
        new_path = os.path.join(temp_dir, 'new_directory')
        assert not os.path.exists(new_path)

        # Call the function to create the path
        create_path_if_not_exist(path=new_path)

        # Check that the path has been created
        assert os.path.exists(new_path)
        assert os.path.isdir(new_path)


def test_path_already_exists():
    with TemporaryDirectory() as temp_dir:
        # Create a path that already exists
        existing_path = temp_dir
        assert os.path.exists(existing_path)
        assert os.path.isdir(existing_path)

        # Call the function on an existing path
        create_path_if_not_exist(path=existing_path)

        # Check that the existing path is still there (unchanged)
        assert os.path.exists(existing_path)
        assert os.path.isdir(existing_path)


def test_write_lines_to_file(tmp_path):
    # Prepare test data
    lines = ['some', 'random', 'text']
    file_name = 'test_file.txt'

    # Call the function
    write_lines_to_file(path=tmp_path, file_name=file_name, lines=lines)

    # Verify that the file has been created and contains the expected content
    file_path = os.path.join(tmp_path, file_name)
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        assert f.read().splitlines() == lines


def test_write_lines_to_existing_file(tmp_path):
    # Prepare test data
    existing_lines = ['some', 'stuff', 'is', 'already', 'there']
    new_lines = ['new', 'stuff']
    file_name = 'existing_file.txt'
    file_path = os.path.join(tmp_path, file_name)

    # Create file
    write_lines_to_file(path=tmp_path, file_name=file_name,
                        lines=existing_lines)

    # try to write into existing file
    write_lines_to_file(path=tmp_path, file_name=file_name, lines=new_lines)

    # Verify that the file has been overwritten and contains the new content
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        assert f.read().splitlines() == new_lines


def test_read_from_nonexistent_pickle_file(tmp_path):
    file_name = 'nonexistent_file.pkl'

    with pytest.raises(FileNotFoundError):  # type: ignore
        read_from_pickle_file(file_name=file_name, path=tmp_path)


def test_save_as_pickle_file(tmp_path):
    # Prepare test data
    transitions = RailEnvTransitions()
    cell_types = transitions.transition_list
    empty = cell_types[0]
    straight = cell_types[1]

    grid = np.array([
        [empty, straight, empty],
        [empty, straight, empty],
        [empty, straight, empty]
    ])
    grid_transition_map = GridTransitionMap(width=grid.shape[1],
                                            height=grid.shape[0],
                                            transitions=transitions)

    optionals = {'agents_hints':
                 {'city_positions': [(0, 1), (2, 1)],
                  'train_stations': [[((0, 1), 0)],
                                     [((2, 1), 0)]],
                  'city_orientations': [2, 0]
                  }
                 }

    environment = RailEnv(width=grid.shape[1],
                          height=grid.shape[0],
                          rail_generator=rail_from_grid_transition_map(
                              grid_transition_map, optionals),
                          line_generator=sparse_line_generator(),
                          number_of_agents=2
                          )
    environment.reset()

    # Create a file that does not exist
    file_name = 'nonexistent_file.pkl'
    file_path = os.path.join(tmp_path, file_name)
    assert not os.path.exists(file_path)

    # Save file
    save_as_pickle_file(file_name=file_name,
                        env=environment, path=tmp_path)

    # Verify the file has been written
    assert os.path.exists(file_path)

    # Load stored environment from file
    new_environment = read_from_pickle_file(file_name=file_name, path=tmp_path)
    new_environment.reset()

    # verify that grids and agents are identical
    assert environment.rail
    assert new_environment.rail
    assert environment.rail.grid.all() == new_environment.rail.grid.all()
    assert environment.agents == new_environment.agents
