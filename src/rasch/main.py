import argparse
from os import path

from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator

from rasch.benchmark import Benchmark
from rasch.logging import get_logger_by_level
from rasch.rasch_config import get_config
from rasch.rasch_setup import solve_and_simulate, solve_with_timeout


def main():
    args = define_args()
    logger = get_logger_by_level(args.loglevel) #get logger for specific level

    try:
        if(args.visualise):
            Benchmark(logger=logger).visualise(args.visualise)
            return
        
        if(args.random):
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
                
            env.reset()

            #TODO: remove if earliest departure more than 0 is supported
            for agent in env.agents:
                agent.earliest_departure = 0

            logger.debug(env._max_episode_steps)
            #TODO: think about a way to change this to solve_with_timeout
            solve_and_simulate(env=env, 
                             env_name="random", 
                             enc_name=args.encoding, 
                             limit=env._max_episode_steps, 
                             norender=args.norender,
                             loglevel=args.loglevel)
            return

        match args.benchmark:
            case 'all': #benchmark all encodings and all environments
                Benchmark(logger=logger).bench_all(args)
            case 'enc': #compare encodings on one environment from config
                Benchmark(logger=logger).bench_encs(args, args.environment)
            case 'env': #compare enviornments on one encoding
                Benchmark(logger=logger).bench_envs(args, enc_name=args.encoding, save=True)
            case _: #else
                
                result_stats = solve_with_timeout(args=args, logger=logger)

                if((args.benchmark == "") & (result_stats == -1)): # -b has no argument, give benchmark for this encoding and env
                    benchmark = Benchmark(logger=logger)
                    benchmark.basic_save(result_stats, name=f"{args.encoding}_{args.environment}")

    except FileNotFoundError as e:
        logger.error(f"{e}")
    except RuntimeError as parse_error:
        if "parsing failed" in str(parse_error):
            logger.error(f"Parsing failed for encoding: {args.encoding}")
            return
        raise

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
