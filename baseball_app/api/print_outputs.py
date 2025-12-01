import pandas as pd
import os

agg_file = "aggregated_data/all_players_MLB_formatted.csv"

metric = "combined"

# 
if os.path.exists(agg_file):
    df = pd.read_csv(agg_file)

    if metric not in df.columns:
        raise ValueError("The combined Metric does not exist in the file")
    
    df_sorted = df.sort_values(by=metric, ascending=False)
    # Keep only the columns we want, rename 'team.csv' to 'team'
    df_sorted = df_sorted.rename(columns={'Player': 'player', 'team.csv': 'team'})
    columns = ['player', 'B', 'Age', 'PO', 'AB', 'team', 'perf', 'use', 'combined']
    df_sorted = df_sorted[columns]

    # Clean up the team column
    df_sorted['team'] = df_sorted['team'].str.rsplit('-', n=1).str[0]
    
    # Add a rank column
    df_sorted.insert(0, 'rank', range(1, len(df_sorted) + 1))
    
    # Print top 60
    print(df_sorted.head(50).to_string(index=False))

