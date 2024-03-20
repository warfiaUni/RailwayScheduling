import multiprocessing as mp
from logging import Logger

from clingo import Control
from flatland.envs.rail_env import RailEnv
from flatland.utils.rendertools import AgentRenderVariant, RenderTool

from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.logging import get_logger_by_level
from rasch.rasch_config import get_config
from rasch.rasch_simulator import RaSchSimulator
from rasch.rasch_solver import RaSchSolver

#TODO: whack name, what is a good name?

def solve_and_simulate(env_name: str, 
                         enc_name: str, 
                         loglevel: str,
                         limit=None,
                         norender: bool = False,
                         result_queue = None,
                         env: RailEnv = None):
     """creates environment and instance, solves it and returns statistics"""
     try:
          logger = get_logger_by_level(loglevel=loglevel)
          if(env is None):
               env = read_from_pickle_file(f'{env_name}.pkl')
               env.reset()
          
          #TODO: remove if earliest departure more than 0 is supported
          for agent in env.agents:
               agent.earliest_departure = 0

          instance_name = f"{enc_name}_{env_name}_instance"
          logger.debug(f"Creating instance: {instance_name}.")
          
          if(limit is None):
               limit = env._max_episode_steps #take flatland Horizon if none defined
               logger.debug(f"Flatland Horizon: {limit}")
          
          instance_lines = generate_instance_lines(env, limit)
     
          write_lines_to_file(file_name=f"{instance_name}.lp",
                              path=get_config().asp_instances_path,
                              lines=instance_lines)

          clingo_control = Control()

          solver = RaSchSolver(environment=env,
                              clingo_control=clingo_control,
                              logger=logger
                              )
          
          solver.solve(encoding_name=enc_name,
                       instance_name=instance_name)
          
          solver.save(file_name=f"{enc_name}_{env_name}_solve.json")

          if(result_queue is not None):
               result_queue.put(True)

          if len(solver.agent_actions.items()) == 0:
               logger.warning(
                    f"No actions generated, check the solver and ASP encoding. ({enc_name}, {env_name})")
               clingo_control.statistics.clear()
               clingo_control.statistics['fl_result'] = "no actions" 

               if(result_queue is not None):
                    result_queue.put(clingo_control.statistics)
               else:
                    return clingo_control.statistics
               
               return None
          
          renderer = RenderTool(
               env, agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS)

          simulator = RaSchSimulator(
               environment=env, renderer=renderer, logger=logger)

          if(simulator.simulate_actions(max_steps=limit,
               agent_actions=solver.agent_actions, render=norender)): # if simulator succeeds
               clingo_control.statistics['fl_result'] = "success"
          else:
               logger.warning(
                    f"Invalid actions, check the actions generator in the encoding. ({enc_name}, {env_name})")
               clingo_control.statistics.clear()
               clingo_control.statistics['fl_result'] = "invalid actions" # actions generated but simulator failed
          
          if(result_queue is not None):
               result_queue.put(clingo_control.statistics)
          else:
               return clingo_control.statistics
     
     except FileNotFoundError as e:
          logger.error(f"{e}")
          return None
     except RuntimeError as parse_error:
          if "parsing failed" in str(parse_error):
               logger.error(f"Parsing failed for encoding: {enc_name} with environment: {env_name}")
          raise

def solve_with_timeout(args, logger):
     result_queue = mp.Queue()
     logger.info(f"Solving {args.environment} with {args.encoding}.")
     process = mp.Process(target=solve_and_simulate, 
                         args=(
                              args.environment, 
                              args.encoding, 
                              args.loglevel,
                              int(args.limit), 
                              args.norender,
                              result_queue))
     process.start()
     process.join(timeout=60)

     #if process is still running and no result was put into queue, terminate it
     if(process.is_alive() & result_queue.empty()):
          logger.warn("Solving timed out.")
          process.terminate()
          process.join()
          result_stats = {}
          result_stats["fl_result"] = "timeout"
          return result_stats
     else: #process is successful
          if(process.is_alive()):
               logger.warn("Simulator is still running.")
          while not result_queue.empty():
               result_stats = result_queue.get() #get last added item
          return result_stats