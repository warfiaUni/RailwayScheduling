import json
import os
from logging import Logger

from clingo.control import Control

from rasch.file import read_from_pickle_file, write_lines_to_file
from rasch.instance_generation import generate_instance_lines
from rasch.rasch_config import RaSchConfig, get_config
from rasch.rasch_solver import RaSchSolver

#TODO: verbose logging option, to remove excess info
#TODO: async

class Benchmark:
     def __init__(self, *,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self._logger = logger
        self._config = config

     def environment_setup(self, 
                           env_name: str, 
                           enc_name: str, 
                           limit=20) -> dict:
          """creates environment and instance, solves it and returns statistics"""
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

               if len(solver.agent_actions.items()) == 0:
                    self._logger.warning(
                         "No actions generated, check the solver and ASP encoding.")

               return clingo_control.statistics
          
          except FileNotFoundError as e:
               self._logger.error(f"{e}")
          except RuntimeError as parse_error:
               if "parsing failed" in str(parse_error):
                    self._logger.error(f"Parsing failed for encoding: {enc_name} with environment: {env_name}")
                    return None
               raise

     def basic_save(self, stats:dict, name = 'test') -> None:
          """save stats from dict to a json"""

          full_path = os.path.join(self._config.statistics_output_path, f'{name}_stats.json')

          self._logger.info(f"Statistics saved to: {full_path}")
          with open(full_path, 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

     def bench_envs(self, args, enc_name: str, save: bool) -> dict:
          """
          benchmark one encoding on all environments found in flatland_environments_path from the config
          """
          env_dir = get_config().flatland_environments_path
          stats = {}

          for env in os.listdir(env_dir): #iterate through environments
               if not env.endswith('.pkl'):
                    continue
               env_name = os.path.splitext(env)[0]
               tmp_stats = self.environment_setup(env_name=env_name, enc_name=enc_name, limit=args.limit) #environment setup
               stats[env_name] = {
                    'summary': tmp_stats['summary'], 
                    'solving': tmp_stats['solving']
               }
          
          if(save):
               _stats = {
                    enc_name: stats
               }
               self.basic_save(stats=_stats, name=enc_name)

          return stats


     def bench_encs(self, args, environment_name: str, save = True) -> dict:
          """
          benchmark one environment on all encodings found in asp_encodings_path from the config
          """
          enc_dir = get_config().asp_encodings_path
          stats = {}

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]
               stats[enc_name] = {}
               stats[enc_name][environment_name] = self.environment_setup(env_name=environment_name, enc_name=enc_name, limit=args.limit) #environment setup

          if(save):
               self.basic_save(stats=stats, name=environment_name)

          return stats

     def bench_all(self, args, save = True) -> dict:
          enc_dir = get_config().asp_encodings_path
          stats = {}

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]

               stats[enc_name] = self.bench_envs(enc_name=enc_name, args=args, save=False)

          if(save):
               self.basic_save(stats=stats, name="all") #save to json
          
          return stats


