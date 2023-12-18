import json
import os
from logging import Logger

from clingo.control import Control

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

     def basic_save(self, clingo_control, name = 'test'):
          stat_path = 'data/statistics/' #TODO: into config
          #output basic stats to file
          stats_times = clingo_control.statistics['summary']['times']
          stats_solver = clingo_control.statistics['solving']['solvers']
          stats = {
               'times': stats_times, 
               'solver': stats_solver
          }

          #print(json.dumps(self.clingo_control.statistics, indent=4,sort_keys=True,separators=(',', ': ')))
          with open(f'{stat_path}{name}_stats.json', 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

     def benchmark_all(self, args):
          enc_dir = get_config().asp_encodings_path
          env_dir = get_config().flatland_environments_path
          stats = {}
          stat_path = 'data/statistics/'

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]
               stats[enc_name] = {}
               for file in os.listdir(env_dir): #iterate through environments
                    if not file.endswith('.pkl'):
                         continue
                    try:
                         name = os.path.splitext(file)[0]

                         env = read_from_pickle_file(f'{file}')
                         env.reset()
                         instance_name = f"{enc_name}_{name}_instance"
                         self._logger.info(f"Creating instance: {instance_name}.")
                         instance_lines = generate_instance_lines(env, args.limit)
                    
                         write_lines_to_file(file_name=f"{instance_name}.lp",
                                             path=get_config().asp_instances_path,
                                             lines=instance_lines)

                         clingo_control = Control()
                         solver = RaSchSolver(environment=env,
                                             clingo_control=clingo_control,
                                             logger=self._logger
                                             )
                         solver.solve(args.encoding,instance_name)
                         solver.save()

                         #save verbose stats #TODO: in tmp directory
                         #self.basic_save(clingo_control, name=f'{encoding}_{name}')

                         stats[enc_name][name] = clingo_control.statistics['summary']['times']['total']

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

          with open(f'{stat_path}stats_total.json', 'w') as f: 
               json.dump(stats, f, indent=4,sort_keys=True,separators=(',', ': '))

               
     

