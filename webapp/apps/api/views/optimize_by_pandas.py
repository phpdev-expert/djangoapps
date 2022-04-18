import pandas as pd
import numpy as np


def data_optimization(metrics,agg,data,pages,metrics_names):
    new_metrics = {}
    for key, value in metrics.items():  # Loop through all dictionary elements in the list
        if key in list(new_metrics):  # if the key already exists, append to new
            for entry in value:
                new_metrics[key].append(entry)
        else:  # if it's a new key, simply add to the new dictionary
            new_metrics[key] = value
    # print(new_metrics['82235273865'])
    metrics_dataframe = pd.DataFrame.from_dict(new_metrics,orient='index')

    # metrics_dataframe = metrics_dataframe.transpose()


    return metrics_dataframe.head(1)