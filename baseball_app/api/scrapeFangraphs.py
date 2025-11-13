import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import sys

def collect_data(team):
    url = f"https://blogs.fangraphs.com/2025-zips-projections-{team}/"

    # Rockies projections is misspelled on fangraphs so use projection instead of projections in url
    if team == "colorado-rockies":
        url = "https://blogs.fangraphs.com/2025-zips-projection-colorado-rockies/"

    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    table_title = soup.find("div", class_="table-title", string="Batters – Standard")
    if not table_title:
        raise ValueError("Could not find 'Batters – Standard' table on the page.")

    table = table_title.find_next("table")

    df = pd.read_html(StringIO(str(table)))[0]

    batters = df.to_dict(orient="records")

    #for b in batters[:5]:
    #    print(b)

    output_path = f"scraped_data/{team}.csv"
    df.to_csv(output_path, index=False)

    # print(f"Data successfully saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrapeFangraphs.py [location-team]")
        sys.exit(1)

    collect_data(sys.argv[1])
