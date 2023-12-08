import sys

from clingo import Control
from flatland.utils.rendertools import AgentRenderVariant, RenderTool

from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.logging import get_logger
from rasch.rasch_config import get_config
from rasch.rasch_simulator import RaSchSimulator
from rasch.rasch_solver import RaSchSolver

logger = get_logger()


def main():
    args = sys.argv[1:]
    try:

        if len(args) < 3:
            args = [get_config().default_encoding,
                    get_config().default_environment,
                    20] #TODO: default_limit

        encoding_name = args[0]
        environment_name = args[1]
        limit = args[2]

        env = read_from_pickle_file(f'{environment_name}.pkl')
        env.reset()

        instance_name = f"{encoding_name}_{environment_name}_instance"
        logger.info(f"Creating instance: {instance_name}.")
        instance_lines = generate_instance_lines(env, limit)
      
        write_lines_to_file(file_name=f"{instance_name}.lp",
                            path=get_config().asp_instances_path,
                            lines=instance_lines)

        clingo_control = Control()
        solver = RaSchSolver(environment=env,
                             clingo_control=clingo_control,
                             logger=logger
                             )
        solver.solve(encoding_name,instance_name)
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
