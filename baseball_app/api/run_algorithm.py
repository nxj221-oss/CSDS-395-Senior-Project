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
output_path = "algorithm_output/"

# Teams and Levels
teams_list = "../all-teams.csv"
levels = ["MLB", "AAA", "AA", "A+", "A"]

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
        clear_data(output_path)

    if fetch_new_data or process_data:
        for team in reader:

            # Scrape the data
            if fetch_new_data:
                # Process MLB team
                os.system(f"python scrape-majors.py {team[0]}")
                
                # Process each of the MiLB affiliate teams (aaa,aa,high-a,single-a,rookie)
                os.system(f"python scrape-minors.py {team[0]} all")

            # Run the algorithm
            if process_data:
                for level in levels:
                    os.system(f"python evaluate_batters.py {scraped_data_path}{team[0]}-{level}.csv {processed_data_path}{team[0]}-{level}.csv")
    
if aggreggate_data:
    # Aggreggate the data
    os.system(f"python aggregate_and_scale.py")

    # Display the outputs
    os.system(f"python print_outputs.py 50")
    print('\nOutput file saved to algorithm_output/all_players_sorted.csv')

