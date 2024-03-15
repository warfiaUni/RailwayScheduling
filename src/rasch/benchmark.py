import json
import os
from logging import Logger
from os import path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from rasch.file import read_from_pickle_file
from rasch.rasch_config import RaSchConfig, get_config
from rasch.rasch_setup import solve_and_simulate

#TODO: (bonus) verbose logging option, to remove excess info
#TODO: (bonus) async
#TODO: add seaborn
#TODO: add timeout as fl_result

class Benchmark:
     def __init__(self, *,
                 logger: Logger,
                 config: RaSchConfig = get_config()) -> None:
        self._logger = logger
        self._config = config

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

               env = read_from_pickle_file(f'{env_name}.pkl') ###
               env.reset() ###
               
               cc = solve_and_simulate(logger=self._logger,env=env,env_name=env_name, enc_name=enc_name, limit=args.limit) #environment setup
               if not hasattr(cc, 'statistics'):
                    continue
               if(cc.statistics['fl_result']=="success"):
                    stats[env_name] = {
                         'fl_result': cc.statistics['fl_result'],
                         'summary': cc.statistics['summary'], 
                         'solving': cc.statistics['solving']
                    }
               else:
                    stats[env_name] = cc.statistics
          
          if(save):
               _stats = {
                    enc_name: stats
               }
               self.basic_save(stats=_stats, name=enc_name)

          return stats


     def bench_encs(self, args, env_name: str, save = True) -> dict:
          """
          benchmark one environment on all encodings found in asp_encodings_path from the config
          """
          enc_dir = get_config().asp_encodings_path
          stats = {}

          for enc in os.listdir(enc_dir): #iterate through encodings
               if not enc.endswith('.lp'):
                    continue
               enc_name = os.path.splitext(enc)[0]

               env = read_from_pickle_file(f'{env_name}.pkl') ###
               env.reset() ###

               stats[enc_name] = {}
               cc = solve_and_simulate(logger=self._logger, env=env, env_name=env_name, enc_name=enc_name, limit=args.limit) #environment setup

               if not hasattr(cc, 'statistics'):
                    continue
               if(cc.statistics['fl_result']=="success"):
                    stats[enc_name][env_name] = {
                         'fl_result': cc.statistics['fl_result'],
                         'summary': cc.statistics['summary'], 
                         'solving': cc.statistics['solving']
                    }
               else:
                    stats[enc_name][env_name] = cc.statistics

          if(save):
               self.basic_save(stats=stats, name=env_name)

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
     
     def visualise(self, file_path = path.join(get_config().statistics_output_path, 'all_stats.json')):
          # Read the nested JSON file
          with open(file_path, 'r') as file:
               stats = json.load(file)

          # create Dataframe readable for seaborn
          lst = []
          for encoding in stats:  
               for environment in stats[encoding]:
                    if(stats[encoding][environment]["fl_result"] == "success"):
                         tmp_lst = [
                              encoding,
                              environment,
                              stats[encoding][environment]["solving"]["solvers"]["choices"],
                              stats[encoding][environment]["solving"]["solvers"]["conflicts"],
                              stats[encoding][environment]["summary"]["times"]["total"],
                              stats[encoding][environment]["summary"]["times"]["solve"],
                              "success"
                         ]
                    else:
                         tmp_lst = [
                              encoding,
                              environment,
                              None,
                              None,
                              None,
                              None,
                              stats[encoding][environment]["fl_result"]
                         ]
                    lst.append(tmp_lst)

          df = pd.DataFrame(lst, columns=["enc","env","choices","conflicts","total","solve", "fl_result"])
          
          # Create a grouped bar plot
          fig, axes = plt.subplots(ncols=2, figsize=(12, 6))

          #Barplot 1
          sns.barplot(x='env', y='choices', hue='enc', data=df, palette='muted', ax=axes[0], legend=False)
          sns.barplot(x='env', y='conflicts', hue='enc', data=df, palette='bright', ax=axes[0])
          axes[0].set(title='Choices and Conflicts', xlabel= 'Environment', ylabel='')    #labels
          axes[0].set_xticks(ticks=axes[0].get_xticks(), labels=axes[0].get_xticklabels(), rotation=45, ha='right') #rotate
          axes[0].legend(title='Encoding')
          for container in axes[0].containers:
               axes[0].bar_label(container, size=6)

          #Barplot 2
          sns.barplot(x='env', y='total', hue='enc', data=df, palette='muted', ax=axes[1], legend=False)
          sns.barplot(x='env', y='solve', hue='enc', data=df, palette='bright', ax=axes[1])
          axes[1].set(title='Total and Solving Time', xlabel='Environment', ylabel='Time [s]')
          axes[1].set_xticks(ticks=axes[1].get_xticks(), labels=axes[1].get_xticklabels(), rotation=45, ha='right') #rotate
          axes[1].legend(title='Encoding')
          for container in axes[1].containers:
               axes[1].bar_label(container, fmt='%.2f', size=6)

          sns.set()
          plt.tight_layout()
          plt.show()


