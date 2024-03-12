import argparse
import logging
from logging import Logger
from os import path

from clingo import Control
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.utils.rendertools import AgentRenderVariant, RenderTool

from rasch.benchmark import Benchmark
from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.logging import get_logger
from rasch.rasch_config import get_config
from rasch.rasch_simulator import RaSchSimulator
from rasch.rasch_solver import RaSchSolver


def main():
    args = define_args()

    match args.loglevel:
        case 'debug':
            logger = get_logger(logging.DEBUG)
        case 'warning':
            logger = get_logger(logging.WARNING)
        case _:
            logger = get_logger(logging.INFO)

    try:
        if(args.visualise):
            Benchmark(logger=logger).visualise(args.visualise)
            return
        
        #TODO: earliest-departure von flatland
        #TODO: doppel debug info
        #TODO: max_steps für simulate_actions
        #TODO: crashing into each other, has something to do with different departure times???
        if(args.random): #TODO
            rail_generator = sparse_rail_generator(max_num_cities=2)

            # Random Environment Generator
            env = RailEnv(
                width=24,
                height=24,
                number_of_agents=2,
                rail_generator=rail_generator,
                line_generator=sparse_line_generator(),
                obs_builder_object=GlobalObsForRailEnv()
            )

            #TODO: remove if earliest departure more than 0 is supported
            for agent in env.agents:
                agent.earliest_departure = 0
                
            env.reset()
            logger.debug(env._max_episode_steps)
            solve_and_render(env=env, 
                             environment_name="random", 
                             encoding_name=args.encoding, 
                             limit=env._max_episode_steps, 
                             logger=logger)

            return

        match args.benchmark:
            case 'all': #benchmark all encodings and all environments
                Benchmark(logger=logger).bench_all(args)
            case 'enc': #compare encodings on one environment from config
                Benchmark(logger=logger).bench_encs(args, args.environment)
            case 'env': #compare enviornments on one encoding
                Benchmark(logger=logger).bench_envs(args, enc_name=args.encoding, save=True)
            case _: #else
                env = read_from_pickle_file(f'{args.environment}.pkl')
                env.reset()
                
                clingo_control = solve_and_render(env=env,
                                                  environment_name=args.environment, 
                                                  encoding_name=args.encoding, 
                                                  limit=env._max_episode_steps,
                                                  logger=logger)

                if((args.benchmark == "") & (clingo_control.statistics is not None)): # -b has no argument, give benchmark for this encoding and env
                    benchmark = Benchmark(logger=logger)
                    benchmark.basic_save(clingo_control.statistics, name=f"{args.encoding}_{args.environment}")

    except FileNotFoundError as e:
        logger.error(f"{e}")
    except RuntimeError as parse_error:
        if "parsing failed" in str(parse_error):
            logger.error(f"Parsing failed for encoding: {args.encoding}")
            return
        raise

def solve_and_render(logger: Logger,
                     env: RailEnv, 
                     environment_name: str, 
                     encoding_name: str, 
                     limit: int = 20, 
                     norender: bool = True) -> Control:

    instance_name = f"{encoding_name}_{environment_name}_instance"
    logger.debug(f"Creating instance: {instance_name}.")
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
        return -1

    renderer = RenderTool(
        env, agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS)

    simulator = RaSchSimulator(
        environment=env, renderer=renderer, logger=logger)

    simulator.simulate_actions(
        agent_actions=solver.agent_actions, render=norender, max_steps=env._max_episode_steps)
    
    return clingo_control

def define_args():
    parser = argparse.ArgumentParser(description='Railway Scheduling with Flatland and ASP')
    parser.add_argument('encoding', default=get_config().default_encoding, nargs='?')
    parser.add_argument('environment', default=get_config().default_environment, nargs='?')
    parser.add_argument('limit', default=20, nargs='?') 
    parser.add_argument('-b','--benchmark', type=str, nargs='?', const='', choices=['','all','env','enc'], help="Activates Benchmarking. This outputs statistics to a file.")
    parser.add_argument('-nr','--norender', action='store_false', help='Flag: Dont visualise actions')
    parser.add_argument('-v', '--visualise', type=str, nargs='?', const=path.join(get_config().statistics_output_path,'all_stats.json'))
    parser.add_argument('-ll', '--loglevel', type=str, nargs='?', choices=['debug','info','warning'], default='info', help='Sets the desired log level.')
    parser.add_argument('-r','--random', action='store_true')
    return parser.parse_args() 
