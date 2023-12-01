import sys
from typing import Optional

from clingo import Control

from rasch.file import read_from_pickle_file
from rasch.logging import get_logger
from rasch.rasch_config import get_config
from rasch.rasch_solver import RaSchSolver

logger = get_logger()


def main():
    args = sys.argv[1:]
    try:

        if len(args) < 2:
            args = [get_config().default_encoding,
                    get_config().default_environment]

        encoding_name = args[0]
        environment_name = args[1]

        env = read_from_pickle_file(f'{environment_name}.pkl')
        clingo_control = Control()
        solver = RaSchSolver(environment=env,
                             clingo_control=clingo_control,
                             logger=logger
                             )
        solver.solve(encoding_name)
        solver.save()
    except FileNotFoundError as e:
        logger.error(f"{e}")
    except RuntimeError as parse_error:
        # Check if the error message indicates "file could not be opened"
        if "parsing failed" in str(parse_error):
            logger.error(f"Parsing failed for encoding: {args[0]}")
            return  # Exit the function without raising the exception

        # If it's a different error, re-raise it
        raise
