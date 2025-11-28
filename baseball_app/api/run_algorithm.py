import csv
import os

# Testing Purposes - Determine which actions to run
fetch_new_data = True # Default: True
process_data = True # Default: True
aggreggate_data = True # Default: True
run_for_one_team = False # Default: False

# Directory Paths
scraped_data_path = "scraped_data/"
processed_data_path = "processed_data/"
aggreggated_data_path = "aggregated_data/"

# Teams and Levels
teams_list = "../all-teams.csv"
levels = ["MLB", "AAA", "AA", "A+", "A", "Rookie"]

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
    if process_data:
        clear_data(processed_data_path)
    
    # Clear out the aggreggated data
    if aggreggate_data:
        clear_data(aggreggated_data_path)

    if fetch_new_data or process_data:
        for team in reader:
            #print(line)
            #team = line[0]

            # Scrape the data
            if fetch_new_data:
                # Process MLB team
                os.system(f"python scrapeFangraphs.py {team[0]}")

                # Process each of the MiLB affiliate teams (aaa,aa,high-a,single-a,rookie)
                for index in range(1, 5):
                    os.system(f"python scrape-minors.py {team[index]} {team[0]} {levels[index]}")


            # Run the algorithm
            if process_data:
                for level in levels:
                    os.system(f"python evaluate_batters.py {scraped_data_path}/{team[0]}-{level}.csv {processed_data_path}/{team[0]}-{level}.csv")

            if run_for_one_team:
                break
    
# Scraping Complete. Aggreggate the data
if aggreggate_data:
    os.system(
    "python aggregate_and_scale.py "
    "--input-dir processed_data "
    "--output-dir aggregated_data "
    "--level MLB"
    )

# TODO: Uncomment
# os.system(f"python print_outputs.py")

