from logging import Logger

from clingo import Control
from flatland.utils.rendertools import AgentRenderVariant, RenderTool

from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.rasch_config import RaSchConfig, get_config
from rasch.rasch_simulator import RaSchSimulator
from rasch.rasch_solver import RaSchSolver

#TODO: finish, and switch out all environment_setups
#TODO: whack name, what is a good name?
class RaSchSetup:
     def __init__(self, *,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self._logger = logger
        self._config = config

     def environment_setup(self, 
                           env_name: str, 
                           enc_name: str, 
                           limit=20) -> Control:
          """creates environment and instance, solves it and returns statistics"""
          try:
               env = read_from_pickle_file(f'{env_name}.pkl')
               env.reset()
               instance_name = f"{enc_name}_{env_name}_instance"
               self._logger.debug(f"Creating instance: {instance_name}.")
               instance_lines = generate_instance_lines(env, limit)
          
               write_lines_to_file(file_name=f"{instance_name}.lp",
                                   path=get_config().asp_instances_path,
                                   lines=instance_lines)

               clingo_control = Control()
               solver = RaSchSolver(environment=env,
                                   clingo_control=clingo_control,
                                   logger=self._logger
                                   )
               solver.solve(enc_name,instance_name)
               solver.save()

               if len(solver.agent_actions.items()) == 0:
                    self._logger.warning(
                         f"No actions generated, check the solver and ASP encoding. ({enc_name}, {env_name})")
                    clingo_control.statistics.clear()
                    clingo_control.statistics['fl_result'] = "no actions" 
                    return clingo_control.statistics

               renderer = RenderTool(
                    env, agent_render_variant=AgentRenderVariant.AGENT_SHOWS_OPTIONS)

               simulator = RaSchSimulator(
                    environment=env, renderer=renderer, logger=self._logger)

               if(simulator.simulate_actions(
                    agent_actions=solver.agent_actions, render=False)): # if simulator succeeds
                    clingo_control.statistics['fl_result'] = "success"
               else:
                    self._logger.warning(
                         f"Invalid actions, check the actions generator in the encoding. ({enc_name}, {env_name})")
                    clingo_control.statistics.clear()
                    clingo_control.statistics['fl_result'] = "invalid actions" # actions generated but simulator failed
               

               return clingo_control
          
          except FileNotFoundError as e:
               self._logger.error(f"{e}")
               return None
          except RuntimeError as parse_error:
               if "parsing failed" in str(parse_error):
                    self._logger.error(f"Parsing failed for encoding: {enc_name} with environment: {env_name}")
               raise