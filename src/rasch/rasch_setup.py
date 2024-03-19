import multiprocessing as mp
import time
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

def solve_and_simulate(logger: Logger, 
                         env: RailEnv,
                         env_name: str, 
                         enc_name: str, 
                         limit=None,
                         norender: bool = False) -> Control:
     """creates environment and instance, solves it and returns statistics"""
     try:
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

          if len(solver.agent_actions.items()) == 0:
               logger.warning(
                    f"No actions generated, check the solver and ASP encoding. ({enc_name}, {env_name})")
               clingo_control.statistics.clear()
               clingo_control.statistics['fl_result'] = "no actions" 

               return clingo_control

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
          
          return clingo_control
     
     except FileNotFoundError as e:
          logger.error(f"{e}")
          return None
     except RuntimeError as parse_error:
          if "parsing failed" in str(parse_error):
               logger.error(f"Parsing failed for encoding: {enc_name} with environment: {env_name}")
          raise

def solve_with_timeout(env_name: str, 
                         enc_name: str, 
                         result_queue: mp.Queue,
                         loglevel: str,
                         limit=None,
                         norender: bool = False):
     
     logger = get_logger_by_level(loglevel=loglevel)
     env = read_from_pickle_file(f'{env_name}.pkl')
     env.reset()

     cc = solve_and_simulate(logger=logger, env=env, env_name=env_name, enc_name=enc_name, limit=limit, norender=norender)

     result_queue.put(cc.statistics)

     return result_queue
