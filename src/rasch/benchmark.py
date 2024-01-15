import json
import os
from logging import Logger

import pandas as pd
from clingo.control import Control
from matplotlib import pyplot as plt

from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.rasch_config import RaSchConfig, get_config
from rasch.rasch_solver import RaSchSolver

#TODO: visualise stats 
#TODO: try all encodings for all environments 
#TODO: don't log if solving fails

class Benchmark:
     def __init__(self, *,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self._logger = logger
        self._config = config

     def environment_setup(self, 
                           env_name: str, 
                           enc_name: str, 
                           stats: list, 
                           limit=20) -> dict:
          try:
               env = read_from_pickle_file(f'{env_name}.pkl')
               env.reset()
               instance_name = f"{enc_name}_{env_name}_instance"
               self._logger.info(f"Creating instance: {instance_name}.")
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

               #save verbose stats #TODO: in tmp directory
               #self.basic_save(clingo_control, name=f'{encoding}_{name}')
               
               #stats[env_name][enc_name] = clingo_control.statistics['solving']['solvers']['choices']

               if len(solver.agent_actions.items()) == 0:
                    self._logger.warning(
                         "No actions generated, check the solver and ASP encoding.")

               return clingo_control.statistics['solving']['solvers']['choices']
          
          except FileNotFoundError as e:
               self._logger.error(f"{e}")
          except RuntimeError as parse_error:
               if "parsing failed" in str(parse_error):
                    self._logger.error(f"Parsing failed for encoding: {enc_name} with environment: {env_name}")
                    return None
               raise

     def basic_save(self, clingo_control, name = 'test') -> None:
          """helper to save basic stats from clingo_control to a file"""
          stat_path = 'data/statistics/' #TODO: into config
          #output basic stats to file
          stats_times = clingo_control.statistics['summary']['times']
          stats_solver = clingo_control.statistics['solving']['solvers']
          stats = {
               'times': stats_times, 
               'solver': stats_solver
          }

          #print(json.dumps(self.clingo_control.statistics, indent=4,sort_keys=True,separators=(',', ': ')))
          self._logger.info(f"Statistics saved to: {stat_path}{name}_stats.json")
          with open(f'{stat_path}{name}_stats.json', 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

     def bench_envs(self, stats: list, enc_name = 'test', limit = 20) -> None:
          """
          benchmark one encoding on all environments found in flatland_environments_path from the config
          
          Parameters
          ----------
          stats : list
               empty list
          enc_name : str
               name of the encoding (.lp-file)
          limit : int
               timestep limit, passed to encoding
          """
          env_dir = get_config().flatland_environments_path
          stat_path = 'data/statistics/'

          for file in os.listdir(env_dir): #iterate through environments
               if not file.endswith('.pkl'):
                    continue
               try:
                    #TODO: environment_setup?
                    name = os.path.splitext(file)[0]

                    env = read_from_pickle_file(f'{file}')
                    env.reset()
                    instance_name = f"{enc_name}_{name}_instance"
                    self._logger.info(f"Creating instance: {instance_name}.")
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

                    #save verbose stats #TODO: in tmp directory
                    #self.basic_save(clingo_control, name=f'{encoding}_{name}')

                    stats[enc_name][name] = clingo_control.statistics['summary']['times']['choices']

                    if len(solver.agent_actions.items()) == 0:
                         self._logger.warning(
                              "No actions generated, check the solver and ASP encoding.")
                         continue

               except FileNotFoundError as e:
                    self._logger.error(f"{e}")
               except RuntimeError as parse_error:
                    if "parsing failed" in str(parse_error):
                         self._logger.error(f"Parsing failed for encoding: {enc_name} with environment: {file}")
                         return
                    raise

     def bench_encs(self, args, environment_name: str) -> None:
          """
          benchmark one environment on all encodings found in asp_encodings_path from the config

          Parameters
          ----------
          args : Namespace
               arguments from argparse
          environment_name : str
               name of the .pkl-file
          """
          enc_dir = get_config().asp_encodings_path
          stat_path = 'data/statistics/'
          stats = {}

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]
               stats[enc_name] = self.environment_setup(env_name=environment_name, enc_name=enc_name, stats=stats, limit=args.limit) #environment setup

          self._logger.info(f"Statistics saved to: {stat_path}_{environment_name}_stats.json")
          with open(f'{stat_path}{environment_name}_stats.json', 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

          self.visualise(stats, environment_name=environment_name)

     def bench_all(self, args):
          enc_dir = get_config().asp_encodings_path
          stats = {}
          stat_path = 'data/statistics/'

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]
               stats[enc_name] = {}

               self.bench_envs(stats=stats, enc_name=enc_name,limit=args.limit)

          self._logger.info(f"Statistics saved to: {stat_path}stats_total.json")
          with open(f'{stat_path}stats_total.json', 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

               
     def visualise(self, stats: dict, environment_name: str):
          #turn dict into series
          s = pd.Series(stats)
          # Create a bar plot
          s.plot(kind='bar')

          # Add labels and title
          plt.xlabel('Encoding')
          plt.ylabel('Number of choices')
          plt.title(environment_name)

          # Display the plot
          plt.show()


