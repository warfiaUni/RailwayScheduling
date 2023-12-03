import sys

from clingo import Control
from flatland.utils.rendertools import AgentRenderVariant, RenderTool

from rasch.file import read_from_pickle_file
from rasch.logging import get_logger
from rasch.rasch_config import get_config
from rasch.rasch_simulator import RaSchSimulator
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
        env.reset()

        clingo_control = Control()
        solver = RaSchSolver(environment=env,
                             clingo_control=clingo_control,
                             logger=logger
                             )
        solver.solve(encoding_name)
        solver.save()

        if len(solver.agent_actions.items()) == 0:
            logger.warning(
                "No actions generated, check the solver and ASP encoding.")
            return

        renderer = RenderTool(
            env, agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS)

        simulator = RaSchSimulator(
            environment=env, renderer=renderer, logger=logger)

        simulator.simulate_actions(
            agent_actions=solver.agent_actions, render=True)

    except FileNotFoundError as e:
        logger.error(f"{e}")
    except RuntimeError as parse_error:
        if "parsing failed" in str(parse_error):
            logger.error(f"Parsing failed for encoding: {args[0]}")
            return
        raise
