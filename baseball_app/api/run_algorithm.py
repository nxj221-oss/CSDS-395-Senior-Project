import csv
import os

# Testing Purposes - Determine which actions to run
fetch_new_data = True
process_data = True
aggreggate_data = True

# Directory Paths
scraped_data_path = "scraped_data/"
processed_data_path = "processed_data/"
aggreggated_data_path = "aggregated_data/"

# File Paths
teams_list = "../teams.csv"

def clear_data(path):
    os.system(f"rm -rf {path}")
    os.system(f"mkdir {path}")

# Read each team
with open(teams_list, newline='') as file:
    reader = csv.reader(file)
    
    # Clear out the scraped data
    if fetch_new_data:
        clear_data(scraped_data_path)

    # Clear out the processed data
    if process_data or fetch_new_data:
        clear_data(processed_data_path)
    
    # Clear out the aggreggated data
    if aggreggate_data:
        clear_data(aggreggated_data_path)

    if fetch_new_data or process_data:
        for line in reader:
            team = line[0]

            # Scrape the data
            if fetch_new_data:
                os.system(f"python scrapeFangraphs.py {team}")

            # Run the algorithm
            if process_data or fetch_new_data:
                os.system(f"python evaluate_batters.py {scraped_data_path}{team}.csv {processed_data_path}{team}.csv")
    
# Scraping Complete. Aggreggate the data
if aggreggate_data:
    os.system(
    "python aggregate_and_scale.py "
    "--input-dir processed_data "
    "--output-dir aggregated_data "
    "--level MLB"
    )

# 
os.system(f"python print_outputs.py")
