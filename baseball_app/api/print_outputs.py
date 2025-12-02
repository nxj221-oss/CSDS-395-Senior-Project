import pandas as pd
import os
import sys

agg_file = "aggregated_data/all_players_ALL_formatted.csv"

metric = "combined"

output_dir = "algorithm_output"
output_file = os.path.join(output_dir, "all_players_sorted.csv")

def sort_and_save(num_to_print: int):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

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
        
        # Add rank column
        df_sorted.insert(0, 'rank', range(1, len(df_sorted) + 1))

        # --- Save ALL sorted players ---
        df_sorted.to_csv(output_file, index=False)

        # --- Print ONLY the top 50 ---
        if num_to_print > 0:
            print(df_sorted.head(num_to_print).to_string(index=False))

    else:
        print(f"{agg_file} does not exist.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python print_outputs.py [number of lines to print]")
        sys.exit(1)
    # parse arguments

    try:
        num = int(sys.argv[1])
    except ValueError:
        print("Second arg must be an integer (number to print).")
        sys.exit(1)

    sort_and_save(num)