import json

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def visualise(file_path = 'data/statistics/all_stats.json'):
    # Read the nested JSON file
    with open(file_path, 'r') as file:
        stats = json.load(file)

    # create Dataframe readable for seaborn
    lst = []
    for encoding in stats:  
        for environment in stats[encoding]:
            tmp_lst = [
                encoding,
                environment,
                stats[encoding][environment]["solving"]["solvers"]["choices"],
                stats[encoding][environment]["solving"]["solvers"]["conflicts"],
                stats[encoding][environment]["summary"]["times"]["total"],
                stats[encoding][environment]["summary"]["times"]["solve"]
            ]
            lst.append(tmp_lst)

    df = pd.DataFrame(lst, columns=["enc","env","choices","conflicts","total","solve"])
    
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