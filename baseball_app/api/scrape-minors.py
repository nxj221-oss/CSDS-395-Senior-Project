import pandas as pd
import sys



def collect_data(team):
    base_url = "https://raw.githubusercontent.com/k-borkowski221/minors-data/main/"
    url = base_url + f"{team}.csv"
    print(url)
    df = pd.read_csv(url)
    print(df.head())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrapeFangraphs.py [location-team]")
        sys.exit(1)

    collect_data(sys.argv[1])