import json
from logging import Logger
from typing import Any, Tuple

from clingo import Model
from clingo.control import Control
from flatland.envs.rail_env import RailEnv

from rasch.file import create_path_if_not_exist
from rasch.rasch_config import RaSchConfig, get_config


class RaSchSolver:
    def __init__(self, *,
                 environment: RailEnv = None,
                 clingo_control: Control,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self.environment = environment
        self._logger = logger
        self._config = config
        self.clingo_control = clingo_control

        self.models = []
        self.agent_actions = {}
        """ Actions each agent is supposed to make."""
        self.agent_paths: dict[Any, list[Tuple[int, int]]] = {}
        """ Path for each agent resulting from the given actions."""
        self.number_of_symbols = 10000

    def _on_clingo_model(self, model: Model):
        """ Populate RaSchASPSolver with data based on found model.

            Args:
                model: Model that was found, which satisfies the provided instance/encoding
        """
        symbols = model.symbols(shown=True)

        self.models.append(
            [f'{symbol.name}({",".join([str(arg) for arg in symbol.arguments])})'
             for symbol in symbols])

        if len(symbols) < self.number_of_symbols:
            self._logger.debug(
                f"Shorter model found {self.number_of_symbols} > {len(symbols)}")
            self.number_of_symbols = len(symbols)
            self.agent_actions = {}
        else:
            return

        for symbol in symbols:
            if symbol.name == "agent_action":
                id = symbol.arguments[0].number
                action = symbol.arguments[1].number
                step = symbol.arguments[2].number

                self.agent_actions.setdefault(id, {})[step] = action

    def solve(self, encoding_name: str, instance_name: str):
        # Load instance from file
        self.clingo_control.load(
            f"{self._config.asp_instances_path}{instance_name}.lp")
        # Load encoding from file
        self.clingo_control.load(
            f"{self._config.asp_encodings_path}{encoding_name}.lp")

        self._logger.debug("Start grounding.")
        self.clingo_control.ground()

        self._logger.debug("Start solving.")
        self.clingo_control.solve(
            on_model=lambda x: self._on_clingo_model(x))
        
        self._logger.debug(
            f"Finished solving, best model has {self.number_of_symbols} symbols.")

    def save(self, file_name: str = "test_solve.json") -> None:
        solve_data = {
            "solution": {
                "agent_paths": self.agent_paths,
                "agent_actions": self.agent_actions
            },
            "models": self.models
        }

        create_path_if_not_exist(path=self._config.solver_output_path)

        with open(f'{self._config.solver_output_path}{file_name}', 'w') as f:
            f.write(json.dumps(solve_data, indent=4))