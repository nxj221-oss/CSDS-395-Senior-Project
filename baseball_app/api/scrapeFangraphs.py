import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://blogs.fangraphs.com/2025-zips-projections-st-louis-cardinals/"

response = requests.get(url)
response.raise_for_status()
html = response.text

soup = BeautifulSoup(html, "html.parser")

table_title = soup.find("div", class_="table-title", string="Pitchers – Standard")
if not table_title:
    raise ValueError("Could not find 'Pitchers – Standard' table on the page.")

table = table_title.find_next("table")

df = pd.read_html(str(table))[0]

pitchers = df.to_dict(orient="records")

for p in pitchers[:5]:
    print(p)