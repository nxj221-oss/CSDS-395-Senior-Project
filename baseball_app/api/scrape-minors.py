import pandas as pd
import sys



def collect_data(team, mlb_team, level):
    base_url = "https://raw.githubusercontent.com/k-borkowski221/minors-data/main/"
    url = base_url + f"{team}.csv"
    df = pd.read_csv(url)
    output_path = f"scraped_data/{mlb_team}-{level}.csv"
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scrape-minors.py [location-team] [location-mlb-team] [level]")
        sys.exit(1)

    collect_data(sys.argv[1], sys.argv[2], sys.argv[3])