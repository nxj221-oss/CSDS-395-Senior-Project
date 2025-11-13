import pandas as pd
import os

agg_file = "aggregated_data/all_players_MLB_formatted.csv"

metric = "combined"

# 
if os.path.exists(agg_file):
    df = pd.read_csv(agg_file)

    if metric not in df.columns:
        raise ValueError("The combined Metric does not exist in the file")
    
    top = df.sort_values(by=metric, ascending=False)
    print(top.head(10))

